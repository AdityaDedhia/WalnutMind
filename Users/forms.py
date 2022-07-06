from tkinter import Widget
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms
from .models import Profile
from django.core.exceptions import ValidationError

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(widget = forms.EmailInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(max_length = 25, widget = forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(max_length = 25, widget = forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

class UpdateUserForm(forms.ModelForm):
        first_name = forms.CharField(max_length = 25, widget = forms.TextInput(attrs={'class':'form-control'}))
        last_name = forms.CharField(max_length = 25, widget = forms.TextInput(attrs={'class':'form-control'}))

        class Meta:
            model = User
            fields = ('first_name', 'last_name', 'email')

        def __init__(self, *args, **kwargs):
            super(UpdateUserForm, self).__init__(*args, **kwargs)
            self.fields['email'].widget.attrs['class'] = 'form-control'
    
class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar','banner', 'interests', 'tags', 'bio', 'meta', 'blog','is_public']

    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].help_text = "Your avatar will be automatically scaled down to 200x200 pixels. You agree that you are the owner of the image uploaded."
        self.fields['banner'].help_text = "Your banner will be automatically scaled down to 1200x600 pixels. You agree that you have legal permission from the owner to use the image uploaded."
        self.fields['avatar'].widget.attrs['class'] = 'form-control'
        self.fields['banner'].widget.attrs['class'] = 'form-control'
        self.fields['interests'].widget.attrs['class'] = 'form-control'
        self.fields['interests'].help_text = "Maximum characters: 75"
        self.fields['bio'].widget.attrs['class'] = 'form-control'
        self.fields['bio'].help_text = "Maximum characters: 300"
        self.fields['meta'].widget.attrs['class'] = 'form-control'
        self.fields['meta'].help_text = "A place to add additional context to your profile. You may also embed widgets such as from Goodreads, Twitter, or other social media accounts."
        self.fields['tags'].widget.attrs['class'] = 'form-control'
        self.fields['tags'].help_text = "Add tags to help people find out what your interests are."
        self.fields['blog'].widget.attrs['class'] = 'form-control'
        self.fields['blog'].help_text = "An optional field that may be helpful for viewers to understand what your blog is about."
        self.fields['is_public'].widget.attrs['class'] = 'form-check-input'


