from django import forms
from .models import Term, List

class NewTermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ('term', 'definition')
        
        widgets = {
            'term': forms.TextInput(attrs={'class': 'form-control'}),
            'definition': forms.Textarea(attrs={'class': 'form-control'}),
        }

class NewListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ('title','description', 'terms')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            
        }
        terms = forms.ModelMultipleChoiceField(queryset=Term.objects.all(), widget=forms.CheckboxSelectMultiple())