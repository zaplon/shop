# -*- coding: utf-8 -*-
from django.forms import ModelForm, Form
from amsoil.models import Order, Shipment, Invoice, User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.shortcuts import render_to_response, RequestContext
from django.core.mail import send_mail
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div

class SelectionForm(Form):
    helper = FormHelper()
    helper.form_tag = False
    helper.form_show_labels = False
    helper.layout = Layout(
        Div(
            Div(
                Div('nazwa', css_class='col-md-6',),
                Div('email',css_class='col-md-6',),
                css_class='row'
            ),
            Div(
                Div('typ', css_class='col-md-6',),
                Div('rok',css_class='col-md-6',),
                css_class='row'
            ),
            Div(
                Div('przebieg', css_class='col-md-6',),
                Div('interwal',css_class='col-md-6',),
                css_class='row'
            ),
            'wielkosc',
            'produkty',
            'styl',
            'inne'
        )
    )
    nazwa = forms.CharField(max_length=50, required=True,
                            widget=forms.TextInput(attrs={'placeholder': 'Imię/nick właściciela*'}))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Email*'}))
    typ = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder': 'Typ i marka pojazdu/maszyny'}))
    rok = forms.CharField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Rok produkcji',
                                                                          'style':'max-width:initial'}))
    przebieg = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Przebieg w tys. km lub setkach godzin'}))
    produkty = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Obecnie stosowane produkty'}))
    interwal = forms.CharField(required=False, max_length=100,
                               widget=forms.TextInput(attrs={'placeholder': 'Obecny i planowany interwał ich wymiany'}))
    wielkosc = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'Wielkość dolewek pomiędzy wymianami w litrach'}))
    styl = forms.CharField(required=False, max_length=50,
                               widget=forms.Textarea(attrs={'rows':3, 'placeholder': 'Styl użytkowania'}))
    inne = forms.CharField(max_length=200, required=False,
                           widget=forms.Textarea(attrs={'rows':3, 'placeholder': 'Inne informacje np. o podwyższeniu mocy silnka'}))


def selectionFormSubmit(request):
    form = SelectionForm(request.POST)
    if form.is_valid():
        if send_mail('Prośba o dobór produktów', form.as_table(), request.POST['email'],
                  ['info@najlepszysyntetyk.pl'], fail_silently=False):
            return render_to_response('selection_success.html', context_instance=RequestContext(request))
        else:
            return render_to_response('index.djhtml',
                                      {'message':'Wystąpił błąd podczas wysyłania wiadomości',
                                       'message_icon':'glyphicon glyphicon-remove'},
                                      context_instance=RequestContext(request))


class InvoiceForm(ModelForm):
    class Meta:
        model = Invoice
        fields = ['NIP','name','address','postalCode','city']
        help_texts = {
            'NIP':'NIP',
            'name':'Nazwa firmy',
            'address':'Adres firmy',
            'postalCode': 'Kod pocztowy',
            'city': 'Miejscowość'
        }


class CheckoutBasicForm(Form):
    email = forms.CharField(max_length=100, widget=forms.EmailInput(attrs={'placeholder': 'Email*'}))
    tel = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Telefon'}))
    help_texts = {
        'email':'Email',
        'tel': 'Telefon'
    }

class ShippingForm(ModelForm):
    class Meta:
        model = Shipment
        fields = ['name', 'surname', 'address', 'postalCode', 'city', 'phone']
        help_texts = {
            'name': 'Imię',
            'email': 'Email',
            'postalCode': 'Kod pocztowy',
            'phone': 'Telefon',
            'address': 'Adres',
            'city': 'Miejscowość',
            'surname': 'Nazwisko'
        }

class UserEditForm(ModelForm):
    class Meta:
        fields = ['email','username']
        model = User

class QuickContactForm(Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Wiadomość', 'rows':'11'}), required=True)