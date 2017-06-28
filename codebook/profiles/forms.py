from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import MyUser, Profile


class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = MyUser
        fields = ['email', 'first_name', 'last_name']


class MyUserChangeForm(UserChangeForm):
    last_login = forms.DateTimeField(disabled=True)

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'first_name', 'last_name', 'is_staff', 'is_active')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('user', 'follows')

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        user = cleaned_data['user']
        following = [profile.user_id for profile in cleaned_data['follows']]
        if user.id in following:
            raise forms.ValidationError("User cannot follow self.")
        return cleaned_data
