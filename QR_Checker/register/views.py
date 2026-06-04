from django.shortcuts import render

def post_register(request):
    return render(request, 'register/post_register.html', {})

