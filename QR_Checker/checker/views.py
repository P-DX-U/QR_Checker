from django.shortcuts import render
from register.models import Post

def check(request):
    return render(request, 'checker/main.html', {})

def get_attendee(request):
    folio = request.GET.get('qr_code')
    attendee = Post.objects.filter(ID=folio).first()
    
    return render(request, 'checker/certificate.html', {'attendee': attendee})