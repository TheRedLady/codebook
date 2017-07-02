from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


MyUser = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = MyUser
        fields = ['first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

        return user
