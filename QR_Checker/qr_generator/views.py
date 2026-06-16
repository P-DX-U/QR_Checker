from django.shortcuts import render
from django.core.paginator import Paginator
from register.models import Post

def attendees_list(request):
    attendees = Post.objects.all()
    paginator = Paginator(attendees, 50)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'qr_generator/registers.html', {'page_obj': page_obj})

