import paypalrestsdk
import json
import urlparse
from django.shortcuts import redirect
from models import Order

#https://devtools-paypal.com/guide/pay_paypal/python?env=sandbox

client_id = 'AQkquBDf1zctJOWGKWUEtKXm6qVhueUEMvXO_-MCI4DQQ4-LWvkDLIN2fGsd'
client_secret = 'EL1tVxAjhT7cJimnz5-Nsx9k2reTKSVfErNQF-CmrwJgxRtylkGTKlU4RvrX'

def paypal_step_1(order):
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
            "return_url": "https://devtools-paypal.com/guide/pay_paypal/python?success=true",
            "cancel_url": "https://devtools-paypal.com/guide/pay_paypal/python?cancel=true"},

        "transactions": [{
                             "amount": {
                                 "total": order.total,
                                 "currency": "PLN"},
                             "description": "creating a payment"}]})


    json_data = payment.create()
    data = json.loads(json_data)
    link = data['links'][1]['href']
    params = urlparse.parse_qs(link)
    order.token = params['token']
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