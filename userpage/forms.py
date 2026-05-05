from django import forms
from .models import *


class OrderForm(forms.ModelForm):
    class Meta:
        model =Order
        fields =['quantity','address','email','phone','payment_method']


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        
