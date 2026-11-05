"""
Parsing of attendee CSV files for the bulk registration workflow.

The CSV must contain the same data as the single register form (post_edit).
Headers may use the model field names (name, last_name, email, ...) or the
Spanish labels shown in the form (Nombre, Apellidos, Correo electrónico, ...).
Header matching ignores case, accents, spaces and underscores.
"""
import csv
import io
import unicodedata
from datetime import datetime

# Order matches the single register form
FIELDS = ['name', 'last_name', 'email', 'event_type', 'role',
          'event_name', 'theme', 'date', 'event_addr']

FIELD_LABELS = {
    'name': 'Nombre',
    'last_name': 'Apellidos',
    'email': 'Correo electrónico',
    'event_type': 'Tipo de evento',
    'role': 'Rol',
    'event_name': 'Nombre del evento',
    'theme': 'Tema',
    'date': 'Fecha',
    'event_addr': 'Dirección del evento',
}

# Extra accepted header spellings (normalized with _normalize)
_EXTRA_ALIASES = {
    'correo': 'email',
    'email': 'email',
    'apellido': 'last_name',
    'evento': 'event_name',
    'direccion': 'event_addr',
    'tipo': 'event_type',
}

# Accepted date formats in the CSV; values are converted to ISO (YYYY-MM-DD)
DATE_FORMATS = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']

MAX_ROWS = 2000


class CsvImportError(Exception):
    """The file cannot be processed at all (encoding, no usable header...)."""


def _normalize(text):
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode()
    return ''.join(ch for ch in text.lower() if ch.isalnum())


_HEADER_MAP = {}
for _field in FIELDS:
    _HEADER_MAP[_normalize(_field)] = _field
    _HEADER_MAP[_normalize(FIELD_LABELS[_field])] = _field
for _alias, _field in _EXTRA_ALIASES.items():
    _HEADER_MAP[_normalize(_alias)] = _field


def _decode(raw_bytes):
    # utf-8-sig handles the BOM Excel adds; cp1252 covers "CSV (Windows)" exports
    for encoding in ('utf-8-sig', 'cp1252'):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise CsvImportError('No se pudo leer el archivo: codificación no soportada (use UTF-8).')


def _normalize_date(value):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    # Leave it untouched: the form reports it as invalid so the user can fix it
    return value


def _normalize_choice(value, choices):
    """Map 'congreso', 'CONGRESO ' ... to the canonical choice value."""
    wanted = _normalize(value)
    for choice_value, _label in choices:
        if _normalize(choice_value) == wanted:
            return choice_value
    return value


def parse_csv(uploaded_file, choices_by_field=None):
    """
    Read an uploaded CSV file and return a dict:
      rows:            list of {'line': <csv line number>, 'data': {field: str}}
      missing_columns: form fields not present in the header
      ignored_columns: header columns that do not match any field
    Blank lines are skipped. Values are stripped; dates are converted to ISO
    and choice fields to their canonical value when possible.
    """
    choices_by_field = choices_by_field or {}
    text = _decode(uploaded_file.read())
    if not text.strip():
        raise CsvImportError('El archivo está vacío.')

    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=',;\t')
    except csv.Error:
        dialect = csv.excel

    reader = csv.reader(io.StringIO(text), dialect)
    try:
        header = next(reader)
    except StopIteration:
        raise CsvImportError('El archivo está vacío.')

    column_map = {}          # column index -> field
    ignored_columns = []
    for index, column in enumerate(header):
        field = _HEADER_MAP.get(_normalize(column))
        if field and field not in column_map.values():
            column_map[index] = field
        elif column.strip():
            ignored_columns.append(column.strip())

    if not column_map:
        raise CsvImportError(
            'No se reconoció ninguna columna. La primera fila debe contener los encabezados: '
            + ', '.join(FIELDS) + '.'
        )

    missing_columns = [f for f in FIELDS if f not in column_map.values()]

    rows = []
    for values in reader:
        if not any(v.strip() for v in values):
            continue
        data = {field: '' for field in FIELDS}
        for index, field in column_map.items():
            data[field] = values[index].strip() if index < len(values) else ''
        if data['date']:
            data['date'] = _normalize_date(data['date'])
        for field, choices in choices_by_field.items():
            if data.get(field):
                data[field] = _normalize_choice(data[field], choices)
        rows.append({'line': reader.line_num, 'data': data})
        if len(rows) > MAX_ROWS:
            raise CsvImportError(f'El archivo excede el máximo de {MAX_ROWS} registros.')

    if not rows:
        raise CsvImportError('El archivo no contiene registros después de los encabezados.')

    return {
        'rows': rows,
        'missing_columns': missing_columns,
        'ignored_columns': ignored_columns,
    }
