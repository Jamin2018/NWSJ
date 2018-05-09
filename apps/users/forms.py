# -*- coding:utf-8 -*-
from django import forms

# from captcha.fields import CaptchaField



from .models import UserProfile



class LoginForm(forms.Form):

    username = forms.CharField(
        required=True,
    )
    password = forms.CharField(
        required=True,
        min_length=8,
    )