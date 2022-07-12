from django import forms
from .models import Term, List, Resource
from dal import autocomplete

class NewTermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ('term', 'definition', 'cover', 'coverSrc', 'coverURL')
        
        widgets = {
            'term': forms.TextInput(attrs={'class': 'form-control'}),
            'definition': forms.Textarea(attrs={'class': 'form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
            'coverSrc': forms.TextInput(attrs={'class': 'form-control'}),
            'coverURL': forms.URLInput(attrs={'class': 'form-control'}),
        }

class NewListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ('title','description', 'terms', 'public')

        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'terms': autocomplete.ModelSelect2Multiple(url='autocompleteterm', attrs={'class': 'form-control'}),
            'public': forms.CheckboxInput(attrs = {'class': 'form-check-input'}),

            #'terms': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class NewResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('title', 'source', 'isbnlink', 'weblink', 'videolink', 'filelink', 'imagelink', 'text', 'description')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'isbnlink': forms.TextInput(attrs={'class': 'form-control'}),
            'weblink': forms.TextInput(attrs={'class': 'form-control'}),
            'videolink': forms.TextInput(attrs={'class': 'form-control'}),
            'filelink': forms.FileInput(attrs={'class': 'form-control'}),
            'imagelink': forms.FileInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }