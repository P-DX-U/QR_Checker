import csv

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, HttpResponseRedirect

import python_utils.p_utils as pu
from .csv_import import CsvImportError, FIELDS, FIELD_LABELS, parse_csv
from .forms import BulkPostForm, CsvUploadForm, PostForm
from .models import Post


def register_string(post):
    # Concatenation without spaces (see "QR_Checker - Register System" note)
    return f"{post.name}{post.last_name}{post.date}{post.event_name}"


def post(request):
    return render(request, 'register/hero_section.html', {})

def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            # Creation of the hash
            post.qr_hash = pu.make_hash(register_string(post))
            post.name = form.cleaned_data['name']
            post.save()
            return HttpResponseRedirect("/thanks/")
    else:
        form = PostForm()
    return render(request, 'register/post_edit.html', {'form': form})


# ---------------------------- Bulk register (CSV) ----------------------------
#
# 1. post_bulk_upload: the CSV is parsed and its rows are kept in the session.
# 2. post_bulk_review: every row is validated with BulkPostForm (same rules as
#    the single register form). Rows with blank/invalid data are shown as
#    editable forms; the operator completes them (or discards them) and
#    revalidates. Corrections are stored back in the session.
# 3. When no invalid rows remain the operator confirms: every row gets its
#    hash (same as post_new) and all registers are saved in one transaction.
#    Rows whose hash already exists in the DB or repeats in the file are skipped.

BULK_SESSION_KEY = 'register_bulk_import'
# Invalid rows rendered as editable forms per page (keeps the POST under
# Django's DATA_UPLOAD_MAX_NUMBER_FIELDS)
EDITABLE_ROWS_PER_PAGE = 50


def _choices_by_field():
    return {
        'event_type': PostForm.Meta.event_choices,
        'role': PostForm.Meta.role_choices,
    }


def _labels():
    return [FIELD_LABELS[f] for f in FIELDS]


def post_bulk_template(request):
    """CSV with the expected headers and an example row."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="plantilla_asistentes.csv"'
    response.write('\ufeff')  # BOM so Excel opens it as UTF-8
    writer = csv.writer(response)
    writer.writerow(FIELDS)
    writer.writerow(['Pancho', 'Villa Arango', 'pancho@example.com', 'Congreso', 'Escucha',
                     'Revolución Mexicana', 'Decena Trágica', '1910-11-20', 'Ciudad de México'])
    return response


def post_bulk_upload(request):
    if request.method == 'POST':
        form = CsvUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                parsed = parse_csv(form.cleaned_data['csv_file'], _choices_by_field())
            except CsvImportError as error:
                form.add_error('csv_file', str(error))
            else:
                for row in parsed['rows']:
                    row['discarded'] = False
                request.session[BULK_SESSION_KEY] = {
                    'filename': form.cleaned_data['csv_file'].name,
                    'rows': parsed['rows'],
                    'missing_columns': parsed['missing_columns'],
                    'ignored_columns': parsed['ignored_columns'],
                    'hashes': {},
                }
                return redirect('post_bulk_review')
    else:
        form = CsvUploadForm()
    return render(request, 'register/bulk_upload.html', {
        'form': form,
        'fields': FIELDS,
        'labels': _labels(),
        'pending': BULK_SESSION_KEY in request.session,
    })


def _apply_post(rows, data):
    """Store the operator's corrections and discard marks in the session rows."""
    shown = {int(i) for i in data.get('shown', '').split(',') if i.isdigit()}
    for index in shown:
        if index >= len(rows):
            continue
        prefix = f'row-{index}'
        rows[index]['discarded'] = data.get(f'{prefix}-discard') == 'on'
        if f'{prefix}-name' in data:  # the row was rendered as an editable form
            rows[index]['data'] = {f: data.get(f'{prefix}-{f}', '').strip() for f in FIELDS}


def _make_hash_cached(post, cache):
    key = register_string(post)
    if key not in cache:
        cache[key] = pu.make_hash(key)
    return cache[key]


def _classify(session_data):
    """Validate every row and split them into invalid / valid / discarded."""
    invalid, valid, discarded = [], [], []
    for index, row in enumerate(session_data['rows']):
        prefix = f'row-{index}'
        form = BulkPostForm({f'{prefix}-{k}': v for k, v in row['data'].items()}, prefix=prefix)
        form.index = index
        form.line = row['line']
        form.values = [row['data'].get(f, '') for f in FIELDS]
        if row['discarded']:
            discarded.append(form)
        elif form.is_valid():
            valid.append(form)
        else:
            invalid.append(form)

    # Hash of each valid row (same as post_new) and duplicate detection
    seen = {}
    for form in valid:
        form.post = form.save(commit=False)
        form.post.qr_hash = _make_hash_cached(form.post, session_data['hashes'])
        form.duplicate_of = seen.get(form.post.qr_hash)
        seen.setdefault(form.post.qr_hash, form.line)
    existing = set(Post.objects.filter(qr_hash__in=list(seen)).values_list('qr_hash', flat=True))
    for form in valid:
        form.exists = form.post.qr_hash in existing
        form.will_save = not form.exists and form.duplicate_of is None
    return invalid, valid, discarded


def post_bulk_review(request):
    session_data = request.session.get(BULK_SESSION_KEY)
    if not session_data:
        messages.warning(request, 'Primero cargue un archivo CSV.')
        return redirect('post_bulk_upload')

    if request.method == 'POST':
        _apply_post(session_data['rows'], request.POST)

    invalid, valid, discarded = _classify(session_data)
    request.session.modified = True  # rows / hash cache were updated in place
    to_save = [f for f in valid if f.will_save]

    if request.method == 'POST' and request.POST.get('action') == 'confirm':
        if invalid:
            messages.error(request, 'Aún hay registros con datos faltantes o inválidos.')
        elif not to_save:
            messages.error(request, 'No hay registros nuevos para guardar.')
        else:
            with transaction.atomic():
                for form in to_save:
                    form.post.save()
            del request.session[BULK_SESSION_KEY]
            summary = f'Se registraron {len(to_save)} asistentes desde "{session_data["filename"]}".'
            if len(valid) > len(to_save):
                summary += f' Se omitieron {len(valid) - len(to_save)} registros duplicados.'
            if discarded:
                summary += f' Se descartaron {len(discarded)} registros.'
            messages.success(request, summary)
            return redirect('post_bulk_upload')

    if request.method == 'POST':
        # Post/Redirect/Get so a browser refresh does not resend the form
        return redirect('post_bulk_review')

    editable = invalid[:EDITABLE_ROWS_PER_PAGE]
    shown = editable + valid + discarded
    return render(request, 'register/bulk_review.html', {
        'filename': session_data['filename'],
        'missing_columns': [FIELD_LABELS[f] for f in session_data['missing_columns']],
        'ignored_columns': session_data['ignored_columns'],
        'labels': _labels(),
        'total': len(session_data['rows']),
        'editable': editable,
        'invalid_count': len(invalid),
        'hidden_invalid_count': len(invalid) - len(editable),
        'valid': valid,
        'discarded': discarded,
        'to_save_count': len(to_save),
        'shown': ','.join(str(f.index) for f in shown),
    })


def post_bulk_cancel(request):
    if request.method == 'POST':
        request.session.pop(BULK_SESSION_KEY, None)
        messages.info(request, 'Importación cancelada.')
    return redirect('post_bulk_upload')
