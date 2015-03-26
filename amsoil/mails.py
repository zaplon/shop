#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from django.core.mail import send_mail
from django.utils import translation
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from shop.settings import FROM_MAIL, CHECKOUT_THANK_YOU
from django.shortcuts import HttpResponse
from amsoil.models import Order
translation.get_language()


def resend_order(request):
    order = Order.objects.get(id=request.GET['id'])
    html = get_template('mail/newOrder.html')
    CHECKOUT_THANK_YOU = """<h2>Szanowny kliencie,</h2>
    <p>Odnotowaliśmy, że z powodu migracji sklepu na nowy serwer, nie udało Ci się złożyć zamówienia
    w sklepie najlepszysyntetyk.pl. Pragnąc poprawić ten błąd przesyłamy poniżej potwierdzenie zamówienia.
    Jeżeli nadal chcesz otrzymać zamówione produkty, proszę potwierdź to odpisując na tę wiadomość bądź
    dzwoniąc pod numer telefonu <strong>502-819-238 </strong>. Prosimy także o przekazanie adresu dostawy</p>
    <p>Za wszystkie powstałe utrudnienia serdecznie przepraszamy i zapraszamy ponownie</p>"""
    c = Context({'request':request, 'order':order, 'thank_you':CHECKOUT_THANK_YOU})
    html = html.render(c)

    send_mail(translation.ugettext('New order'), translation.ugettext('New order'), FROM_MAIL,
              (order.email,), fail_silently=False, html_message=html)

    return HttpResponse(json.dumps({'success':True}),  content_type='application/json')


def newOrder(order, request):

    html = get_template('mail/newOrder.html')
    c = Context({'request':request, 'order':order, 'thank_you':CHECKOUT_THANK_YOU})
    html = html.render(c)

    send_mail(translation.ugettext('New order'), translation.ugettext('New order'), FROM_MAIL,
              (order.email,), fail_silently=False, html_message=html)


def orderNotification(order, request):
    html = get_template('mail/orderNotification.html')
    c = Context({'request':request,'order':order})
    html = html.render(c)

    send_mail('Nowe zamówienie', translation.ugettext('New order'), FROM_MAIL,
              ('janek.zapal@gmail.com',FROM_MAIL,), fail_silently=False, html_message=html)



def newsletter_register_mail(request,email, token):
    html = get_template('mail/newsletter_register.html')
    c = Context({'request':request, 'email':email, 'token':token})
    html = html.render(c)

    send_mail('Rejestracja do systemu newsletter', 'Rejestracja do systemu newsletter', FROM_MAIL,
              (email,), fail_silently=False, html_message=html)
