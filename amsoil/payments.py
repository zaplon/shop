import paypalrestsdk


def paypal(order):
    paypalrestsdk.configure({
        'mode': 'sandbox',
        'client_id': 'AQkquBDf1zctJOWGKWUEtKXm6qVhueUEMvXO_-MCI4DQQ4-LWvkDLIN2fGsd',
        'client_secret': 'EL1tVxAjhT7cJimnz5-Nsx9k2reTKSVfErNQF-CmrwJgxRtylkGTKlU4RvrX'
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
                                 "total": order.cart.getTotal(),
                                 "currency": "PLN"},
                             "description": "creating a payment"}]})


    payment.create()


