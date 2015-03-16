import paypalrestsdk
import json
import urlparse
from django.shortcuts import redirect
from models import Order

from django.views.generic.detail import DetailView
from getpaid.forms import PaymentMethodForm
from amsoil.models import Order
from getpaid import signals

def payment_status_changed_listener(sender, instance, old_status, new_status, **kwargs):
    """
    Here we will actually do something, when payment is accepted.
    E.g. lets change an order status.
    """
    if old_status != 'paid' and new_status == 'paid':
        # Ensures that we process order only one
        instance.order.status = 'P'
        instance.order.save()

signals.payment_status_changed.connect(payment_status_changed_listener)

def new_payment_query_listener(sender, order=None, payment=None, **kwargs):
    """
    Here we fill only two obligatory fields of payment, and leave signal handler
    """
    payment.amount = order.total
    payment.currency = 'PLN'

signals.new_payment_query.connect(new_payment_query_listener)
