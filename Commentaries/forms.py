from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'author','isbn', 'year', 'pages', 'cover', 'tags','rating', 'headquote', 'abstract', 'quotes', 'takeaways', 'summary', 'content', 'resources', 'public')
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn':forms.TextInput(attrs={'class': 'form-control','placeholder':'Optional - isbndb.com'}),
            'pages': forms.NumberInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.Select(choices=Post.RATING_CHOICES, attrs={'class':'form-control'}),
            'headquote': forms.TextInput(attrs={'class': 'form-control','placeholder':'"Quote..."'}),
            'abstract': forms.TextInput(attrs={'class': 'form-control'}),
            'quotes': forms.Textarea(attrs={'class': 'form-control','rows':4,'placeholder': '"Quote 1..."\n"Quote 2..."\n"Quote 3..."'}),
            'takeaways': forms.Textarea(attrs={'class': 'form-control','rows':4,'placeholder': '1.\n2.\n3.'}),
            'summary': forms.Textarea(attrs={'class': 'form-control','rows':4, 'placeholder':'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc velit ante, blandit quis faucibus id, placerat sit amet quam. Donec nec egestas turpis, ut tempus urna. Vestibulum in luctus dui, dictum faucibus libero.'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'resources': forms.Textarea(attrs={'class': 'form-control'}),
            'public': forms.CheckboxInput(attrs = {'class': 'form-check-input'}),
        }