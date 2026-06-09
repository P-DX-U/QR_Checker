from django.shortcuts import render, HttpResponseRedirect
from .forms import PostForm


def post(request):
    return render(request, 'register/hero_section.html', {})

def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.name = form.cleaned_data['name']
            post.save()
            return HttpResponseRedirect("/thanks/")
    else:
        form = PostForm()
    return render(request, 'register/post_edit.html', {'form': form})