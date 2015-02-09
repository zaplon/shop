#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.mail import send_mail
from django.utils import translation
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from shop.settings import FROM_MAIL, CHECKOUT_THANK_YOU
translation.get_language()


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
              ('janek.zapal@gmail.com',), fail_silently=False, html_message=html)
