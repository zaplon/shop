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
    c = Context({'request':request, 'order':order, 'thank_you':CHECKOUT_THANK_YOU})
    html = html.render(c)

    send_mail(translation.ugettext('New order'), translation.ugettext('New order'), FROM_MAIL,
              (order.email,), fail_silently=False, html_message=html)

    return HttpResponse(json.dumps({'success':True}),  content_type='application/json')


def newOrder(order, request):

    html = get_template('mail/newOrder.html')
    c = Context({'request':request, 'order':order, 'thank_you':CHECKOUT_THANK_YOU})
    html = html.render(c)

    if send_mail(translation.ugettext('New order'), translation.ugettext('New order'), FROM_MAIL,
              (order.email,), fail_silently=False, html_message=html):
        order.mail_sended = True
        order.save()


def orderNotification(order, request):
    html = get_template('mail/orderNotification.html')
    c = Context({'request':request,'order':order})
    html = html.render(c)

    send_mail('Nowe zamówienie', translation.ugettext('New order'), FROM_MAIL,
              (FROM_MAIL,'zamowienia@najlepszysyntetyk.pl'), fail_silently=False, html_message=html)



def newsletter_register_mail(request,email, token):
    html = get_template('mail/newsletter_register.html')
    c = Context({'request':request, 'email':email, 'token':token})
    html = html.render(c)

    send_mail('Rejestracja do systemu newsletter', 'Rejestracja do systemu newsletter', FROM_MAIL,
              (email,), fail_silently=False, html_message=html)
