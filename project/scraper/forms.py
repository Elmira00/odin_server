from django import forms

class ExportNewsArticlesForm(forms.Form):
    date = forms.DateField(
        required=True,
        label="Date for Create Excel",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'vDateField'
        })
    )