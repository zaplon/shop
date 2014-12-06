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
        fields = ['name', 'surname', 'address', 'phone']

class UserEditForm(ModelForm):
    class Meta:
        model = User

class QuickContactForm(Form):
    email = forms.EmailField(required=True)
    body = forms.CharField(widget=forms.Textarea)