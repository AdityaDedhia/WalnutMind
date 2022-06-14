from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'cover', 'coverSrc', 'coverURL', 'abstract','tags', 'content', 'resources')
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
            'abstract': forms.TextInput(attrs={'class': 'form-control'}),
            'coverSrc': forms.TextInput(attrs={'class': 'form-control'}),
            'coverURL': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'resources': forms.Textarea(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.Form):
    content = forms.CharField()
    pk = forms.IntegerField()