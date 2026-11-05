from django import forms
from .models import Post
from .csv_import import FIELD_LABELS

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

class CsvUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Archivo CSV',
        widget=forms.ClearableFileInput(attrs={
            'accept': '.csv,text/csv',
            'class': 'block w-full text-sm text-gray-900 file:mr-4 file:rounded-md file:border-0 file:bg-indigo-600 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-indigo-500',
        }),
    )

    MAX_UPLOAD_SIZE = 5 * 1024 * 1024

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        if not csv_file.name.lower().endswith('.csv'):
            raise forms.ValidationError('El archivo debe tener extensión .csv')
        if csv_file.size > self.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('El archivo excede el tamaño máximo de 5 MB.')
        return csv_file


class BulkPostForm(PostForm):
    """
    PostForm used for every row of a CSV import. Same fields and widgets, but
    event_type and role are validated against the allowed choices (the select
    widget would otherwise silently replace an unknown CSV value), and an empty
    option is added so missing values are reported instead of defaulted.
    """
    event_type = forms.ChoiceField(
        choices=(('', '---------'),) + PostForm.Meta.event_choices,
        widget=PostForm.Meta.widgets['event_type'].__class__(attrs=PostForm.Meta.widgets['event_type'].attrs),
    )
    role = forms.ChoiceField(
        choices=(('', '---------'),) + PostForm.Meta.role_choices,
        widget=PostForm.Meta.widgets['role'].__class__(attrs=PostForm.Meta.widgets['role'].attrs),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.label = FIELD_LABELS.get(name, field.label)
        self.fields['date'].input_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
        self.fields['date'].widget.format = '%Y-%m-%d'
