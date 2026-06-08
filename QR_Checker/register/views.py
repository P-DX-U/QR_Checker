from django.shortcuts import render, redirect
from .forms import PostForm


def post(request):
    return render(request, 'register/hero_section.html', {})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = PostForm()
    return render(request, 'register/post_edit.html', {'form': form})