from django.shortcuts import render, redirect
from register.models import Post

def check(request):
    return render(request, 'checker/main.html', {})

def get_attendee(request):
    folio = request.GET.get('qr_code', '').strip()
    attendee = Post.objects.filter(ID=folio).first() if folio.isdigit() else None

    if attendee is None:
        return render(request, 'checker/certificate.html', {'attendee': None})

    # Same URL form embedded in the QR code: <server_ip>/checkin/<hash>
    return redirect('certificate', attendee_hash=attendee.qr_hash.strip())

def certificate(request, attendee_hash):
    attendee_hash = attendee_hash.strip()
    # Hashes are stored with a trailing newline (see python_utils.make_hash)
    attendee = Post.objects.filter(qr_hash__in=[attendee_hash, attendee_hash + '\n']).first()

    return render(request, 'checker/certificate.html', {'attendee': attendee})
