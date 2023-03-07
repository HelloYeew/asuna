from django import forms

from apps.models import Project, LANGUAGES


class CreateProjectForm(forms.ModelForm):
    name = forms.CharField(
        label='Project Name',
        help_text='The name of the project.',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'mother-rosario'})
    )

    description = forms.CharField(
        label='Project Description',
        help_text='The description of the project.',
        max_length=200,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'A project that does something...'})
    )

    source = forms.URLField(
        label='Project Source',
        help_text="The link to your project's source code.",
        max_length=200,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/asuna/mother-rosario'})
    )

    language = forms.ChoiceField(
        label='Language',
        help_text='Language and test framework used in the project.',
        choices=LANGUAGES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'source', 'language']


class UploadKeyRenewConfirmationForm(forms.Form):
    password = forms.CharField(
        label='Password',
        help_text='Your password.',
        max_length=50,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError('Incorrect password.')
        return password
