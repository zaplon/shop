# -*- coding: utf-8 -*-
from django.forms import ModelForm, Form
from amsoil.models import Order, Shipment, Invoice, User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class InvoiceForm(ModelForm):
    class Meta:
        model = Invoice
        fields = ['NIP','name','address']
        help_texts = {
            'NIP':'NIP',
            'name':'Nazwa firmy',
            'address':'Adres firmy'
        }


class CheckoutBasicForm(Form):
    email = forms.CharField(max_length=100, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    tel = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Telefon'}))
    help_texts = {
        'email':'Email',
        'tel': 'Telefon'
    }

class ShippingForm(ModelForm):
    class Meta:
        model = Shipment
        fields = ['name', 'surname', 'address','postalCode', 'phone']
        help_texts = {
            'name': 'Imię',
            'email': 'Email',
            'postalCode': 'Kod pocztowy',
            'phone': 'Telefon',
            'address': 'Adres',
            'surname': 'Nazwisko'
        }

class UserEditForm(ModelForm):
    class Meta:
        fields = ['email','username']
        model = User

class QuickContactForm(Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Wiadomość', 'rows':'11'}), required=True)