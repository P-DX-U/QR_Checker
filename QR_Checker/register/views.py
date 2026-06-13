from django.shortcuts import render, HttpResponseRedirect

import python_utils.p_utils as pu
from .forms import PostForm


def post(request):
    return render(request, 'register/hero_section.html', {})

def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            # Creation of the register string
            register_string = f"{post.name}{post.last_name}{post.date}{post.event_name}"
            # Creation of the hash
            post.qr_hash = pu.make_hash(register_string)
            post.name = form.cleaned_data['name']
            post.save()
            return HttpResponseRedirect("/thanks/")
    else:
        form = PostForm()
    return render(request, 'register/post_edit.html', {'form': form})