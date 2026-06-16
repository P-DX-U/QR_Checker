from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from register.models import Post
import python_utils.p_utils as pu

def attendees_list(request):
    attendees = Post.objects.all()
    paginator = Paginator(attendees, 50)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'qr_generator/registers.html', {'page_obj': page_obj})

def delete_register(request, attendee_hash):
    if request.method == 'POST':
        try:
            attendee = Post.objects.get(qr_hash=attendee_hash)
            attendee.delete()
        except Post.DoesNotExist:
            pass
    return redirect('attendees_list')

def create_url(request, attendee_hash):
    if request.method == 'POST':
        try:
            attendee = Post.objects.get(qr_hash=attendee_hash)
            reference_url = request.build_absolute_uri('/')[:-1] + '/checkin/' + attendee.qr_hash

        except Post.DoesNotExist:
            pass   
    return redirect('attendees_list')

def create_qr(request, attendee_hash):
    if request.method == 'POST':
        try:
            attendee = Post.objects.get(qr_hash=attendee_hash)
            reference_url = request.build_absolute_uri('/')[:-1] + '/checkin/' + attendee.qr_hash
            pu.create_qr_code(reference_url, f"{attendee.qr_hash}.png")
        except Post.DoesNotExist:
            pass   
    return redirect('attendees_list')
