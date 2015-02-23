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


#https://devtools-paypal.com/guide/pay_paypal/python?env=sandbox

#user
#client_id = 'AcFQ22eerOUkPEWvKohBb3Pa2LUhLVjFYISwsXki6K38e_SYy1so-ZTZJbAeqhE6vCb4ALpm2377J5ed'
#client_secret = 'EO-aiZGoaQCyPKm_OjdFHuvmfEUlfr69sbVQIfVAn3uYco3iZdRfiFPp0yeRGmNN3dnhvf5LNYRaJ9Ft'

#app
client_id = 'AQ3y0RAPNZ_J2HJqCFX9e5pECIx_6t1p1UFdmtYA_--7CZDmZLIAuJLla2_n'
client_secret = 'EHXM0BDLoYpRi0o-1ynYmKFbcpmcZrJCUeaHx7p9--ACFxZ3I11wcyMGAr82'

def paypal_step_1(order,request):
    paypalrestsdk.configure({
        'mode': 'sandbox',
        'client_id': client_id,
        'client_secret': client_secret
    })

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": 'http:/zaplon.webfactional.com/zamowienia'+"?success=true",
            "cancel_url": 'http:/zaplon.webfactional.com/zamowienia'+"?cancel=true"},
        "transactions": [{
                             "amount": {
                                 "total": order.total,
                                 "currency": "PLN"},
                             "description": "creating a payment"}]})


    status = payment.create()
    data = payment.to_dict()
    link = data['links'][1]['href']
    params = urlparse.parse_qs(link)
    order.token = params['token']
    order.save()
    return redirect(link)

def paypal_step_2(request):
    try:
        payment_id = request.GET['paymentId']
        payer_id =  request.GET['PayerID']
        success = request.GET['success']
        token = request.GET['token']
    except:
        return False
    if not success:
        return False
    payment = paypalrestsdk.Payment.find(payment_id)
    json_data = payment.execute({"payer_id": payer_id})
    order = Order.objects.get(token=token)
    order.paypalData = json_data
    return order
    #data = json.loads(json_data)
