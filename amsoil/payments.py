import paypalrestsdk
import json
import urlparse
from django.shortcuts import redirect
from models import Order

#https://devtools-paypal.com/guide/pay_paypal/python?env=sandbox

#nasze dane sandbox
client_id = 'AcFQ22eerOUkPEWvKohBb3Pa2LUhLVjFYISwsXki6K38e_SYy1so-ZTZJbAeqhE6vCb4ALpm2377J5ed'
client_secret = 'EO-aiZGoaQCyPKm_OjdFHuvmfEUlfr69sbVQIfVAn3uYco3iZdRfiFPp0yeRGmNN3dnhvf5LNYRaJ9Ft'

client_id = 'AQ3y0RAPNZ_J2HJqCFX9e5pECIx_6t1p1UFdmtYA_--7CZDmZLIAuJLla2_n'
client_secret = 'EHXM0BDLoYpRi0o-1ynYmKFbcpmcZrJCUeaHx7p9--ACFxZ3I11wcyMGAr82'

#sandbox
#client_id = 'AQ3y0RAPNZ_J2HJqCFX9e5pECIx_6t1p1UFdmtYA_--7CZDmZLIAuJLla2_n'
#client_secret = 'EHXM0BDLoYpRi0o-1ynYmKFbcpmcZrJCUeaHx7p9--ACFxZ3I11wcyMGAr82'


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
            "return_url": request.build_absolute_uri()[0:-1]+"?success=true",
            "cancel_url": request.build_absolute_uri()[0:-1]+"?cancel=true"},
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