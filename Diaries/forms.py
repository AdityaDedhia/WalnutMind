from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'cover', 'coverSrc', 'coverURL', 'tags', 'content', 'public')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'coverSrc': forms.TextInput(attrs={'class': 'form-control'}),
            'coverURL': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }
