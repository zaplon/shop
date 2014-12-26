# -*- coding: utf-8 -*-
from django.forms import ModelForm, Form
from amsoil.models import Order, Shipment, Invoice, User
from django.contrib.auth.forms import UserCreationForm
from django import forms


class InvoiceForm(ModelForm):
    class Meta:
        model = Invoice
        fields = ['NIP','name','address']

class ShippingForm(ModelForm):
    class Meta:
        model = Shipment
        fields = ['name', 'surname', 'address','postalCode', 'phone']

class UserEditForm(ModelForm):
    class Meta:
        model = User

class QuickContactForm(Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Wiadomość', 'rows':'11'}), required=True)