from django import forms
from .models import Term

class NewTermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ('term', 'definition')
        
        widgets = {
            'term': forms.TextInput(attrs={'class': 'form-control'}),
            'definition': forms.Textarea(attrs={'class': 'form-control'}),
        }