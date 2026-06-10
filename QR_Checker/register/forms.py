from django import forms
from .models import Post

class DateInput(forms.DateInput):
    input_type = 'date'

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['name', 'last_name', 'email', 'event_type', 'role', 'event_name', 'theme', 'date', 'event_addr']
        event_choices = (('Diplomado','Diplomado'), ('Congreso','Congreso'), ('Seminario', 'Seminario'),)
        role_choices = (('Escucha','Escucha'), ('Ponente', 'Ponente'))
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                'placeholder': 'Pancho',
                'maxlength': '100'
            }),

            'last_name': forms.TextInput(attrs={
                'class' : 'block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                'placeholder': 'Villa',
                'maxlength': '100'
            }),

            'email': forms.EmailInput(attrs={
                'class' : 'block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                'maxlength': '254'
            }),
            
            'event_type': forms.Select(choices = event_choices, attrs={
                'class': 'form-control col-start-1 row-start-1 w-full appearance-none rounded-md bg-white py-1.5 pr-8 pl-3 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
            }),

            'role': forms.Select(choices = role_choices, attrs={
                'class' : 'form-control col-start-1 row-start-1 w-full appearance-none rounded-md bg-white py-1.5 pr-8 pl-3 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
            }),

            'event_name' : forms.TextInput(attrs={
                'class' : 'block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                'maxlength': '256'
            }),
            
            'theme' : forms.TextInput(attrs={
                'class' : 'col-start-1 row-start-1 w-full appearance-none rounded-md bg-white py-1.5 pr-8 pl-3 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                'maxlength' : '256'
            }),

            'date' : DateInput(attrs={
                'class' : 'form-control block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                'maxlength' : '256'
            }),

            'event_addr' : forms.TextInput(attrs={
                'class' : 'block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                'maxlength' : '256'
            }),
        }