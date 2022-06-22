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
        fields = ['avatar','banner', 'interests', 'bio']

    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].help_text = "Your avatar will be automatically scaled down to 200x200 pixels. You agree that you are the legal owner of the image uploaded."
        self.fields['banner'].help_text = "Your banner will be automatically scaled down to 1200x600 pixels. You agree that you have legal permission from the owner to use the image uploaded."
        self.fields['avatar'].widget.attrs['class'] = 'form-control'
        self.fields['banner'].widget.attrs['class'] = 'form-control'
        self.fields['interests'].widget.attrs['class'] = 'form-control'
        self.fields['interests'].help_text = "Maximum characters: 75"
        self.fields['bio'].widget.attrs['class'] = 'form-control'
        self.fields['bio'].help_text = "Maximum characters: 300"

