#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.mail import send_mail
from django.utils import translation
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from shop.settings import FROM_MAIL
translation.get_language()


def newOrder(order, request):

    html = get_template('mail/newOrder.html')
    c = Context({'request':request})
    html = html.render(c)

    send_mail(translation.ugettext('New order'), html, FROM_MAIL,
              (order.email,), fail_silently=False)


def orderNotification(order, request):
    html = get_template('mail/orderNotification.html')
    c = Context({'request':request})
    html = html.render(c)

    send_mail('Nowe zamówienie', html, FROM_MAIL,
              ('janek.zapal@gmail.com',), fail_silently=False)
