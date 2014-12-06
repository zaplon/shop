from django.core.mail import send_mail
from django.utils import translation
from django.shortcuts import render
from django.template.loader import get_template
from shop.settings import FROM_MAIL
translation.get_language()


def newOrder(receiver):

    html = get_template('mail/newOrder.html')
    c = {}
    html = html.render(c)

    send_mail(translation.ugettext('New order'), html, FROM_MAIL,
    receiver, fail_silently=False)