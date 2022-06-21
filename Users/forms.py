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
    
class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'location', 'interests', 'bio']
