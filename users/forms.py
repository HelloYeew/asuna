from django import forms

from users.models import THEME_SETTINGS, Settings


class UserSettingsForm(forms.ModelForm):
    """Form for user settings page"""
    theme = forms.ChoiceField(
        label='Theme',
        help_text='Set the theme for Asuna.',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        choices=THEME_SETTINGS
    )

    class Meta:
        model = Settings
        fields = ['theme']
