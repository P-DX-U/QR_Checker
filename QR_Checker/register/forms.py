from django import forms
from .models import Post

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['name', 'event_type', 'role', 'event_name', 'theme', 'date', 'event_addr']
    