from django.shortcuts import render

def check(request):
    return render(request, 'checker/main.html', {})

