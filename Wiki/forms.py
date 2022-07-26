from django import forms
from .models import Term, List, Resource, Collection
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

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('title', 'source', 'isbnlink', 'weblink', 'webicon', 'webdescription', 'videolink', 'videolength', 'videothumbnail', 'videochannel', 'videodescription', 'filelink', 'filetype', 'text', 'category', 'description', 'public')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'isbnlink': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter an ISBN-13 code'}),
            'weblink': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a valid web URL'}),
            'filelink': forms.FileInput(attrs={'class': 'dropzone', 'type': 'file', 'accept': 'image/*, video/*, audio/*, application/pdf'}),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a description'}),
            'public': forms.CheckboxInput(attrs = {'class': 'form-check-input form-control'}),
        }

class DocForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('title','source','text','description','public')

        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title (Optional)'}),
            'public': forms.CheckboxInput(attrs = {'class': 'form-check-input'}),
        }

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ('title', 'cover', 'description', 'public')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'public': forms.CheckboxInput(attrs = {'class': 'form-check-input'}),

        }