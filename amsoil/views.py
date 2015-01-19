#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, RequestContext, HttpResponse, HttpResponseRedirect, render
from amsoil.models import Page, Product, Cart, User, CartProduct, ProductVariation, \
    ShippingMethod, PaymentMethod, Order, Invoice, Shipment, Category
from rest_framework import viewsets
from amsoil.serializers import ProductSerializer, PaymentMethodSerializer, ShippingMethodSerializer, \
    CartSerializer, CartProductSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import django_filters, json, datetime
from django.contrib.auth import authenticate, login, logout
from amsoil.forms import ShippingForm, InvoiceForm, QuickContactForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum
from django.core import serializers
from django.core.mail import send_mail
from django.db.models import Q

from amsoil.mails import newOrder


def home(request):
    return render_to_response('index.djhtml', {}, context_instance=RequestContext(request))

def page(request, id):
    page = Page.objects.get(id=id)
    return render_to_response('page.html', {'page':page}, context_instance=RequestContext(request))


def shop(request):
    path = request.path.split('/')

    try:
        cat_ind = path.index('category')
        category_id = Category.objects.get(name = path[cat_ind+1]).id
        return render_to_response('shop.djhtml', {'category_id': category_id}, context_instance=RequestContext(request))
    except:
        return render_to_response('shop.djhtml', {}, context_instance=RequestContext(request))

def cart(request):
    return render_to_response('cartView.html', [], context_instance=RequestContext(request))

def register(request):
    return render_to_response('registerView.html', {'form':UserCreationForm}, context_instance=RequestContext(request))

def account(request):
    us = request.user
    try:
        invoice = InvoiceForm(instance=Invoice.objects.get(user = us))
    except:
        invoice = InvoiceForm()
    try:
        payer = ShippingForm(instance=Shipment.objects.get(user = us, type='PA'))
    except:
        payer = ShippingForm()
    try:
        shipment = ShippingForm(instance=Shipment.objects.get(user = us, type='RE'))
    except:
        shipment = ShippingForm()

    if request.method == 'POST':
        if request.POST['type'] == 'invoice':
            invoice = InvoiceForm(request.POST)
            if invoice.is_valid():
                inv = invoice.save(commit=False)
                inv.user = us
                inv.save()
        if request.POST['type'] == 'payer':
            payer = ShippingForm(request.POST)
            if payer.is_valid():
                pay = payer.save(commit=False)
                pay.user = us
                pay.type = 'PA'
                pay.save()
        if request.POST['type'] == 'shipment':
            shipment = ShippingForm(request.POST)
            if shipment.is_valid():
                shi = shipment.save(commit=False)
                shi.type = 'RE'
                shi.user = us
                shi.save()

    if request.user.is_authenticated():
        orders = Order.objects.filter(user = request.user)
    else:
        orders = []

    return render_to_response('myAccount.html', {
        'userChangeForm': '', #UserChangeForm(us),
        'invoiceForm': invoice,
        'shipmentForm': shipment,
        'payerForm': payer,
        'orders': orders,
    }, context_instance=RequestContext(request) )


def processOrder(data):
    pass


def takeCart(request):
    cart = Cart.objects.get(id = request.POST['id'])
    request.session['cartId'] = cart.id
    return HttpResponse(json.dumps({'success':True}))

def minicart(request):
    if 'cartId' in request.session:
        items = CartProduct.objects.filter(cart__id = request.session['cartId'])
        return HttpResponse(json.dumps({
            'items': CartProductSerializer(items, many=True).data,
            'total':  str(items.aggregate(
                total = Sum('price', field="price*quantity"))['total']) + 'zł',
            'count' : items.aggregate(Sum('quantity')).values()[0]
        }))
    else:
        return HttpResponse(json.dumps({
            'items': [],
            'total': 0,
            'count' : 0,
        }))



def checkout(request):
    if request.method == 'POST':
        hasErrors = False
        data = json.loads(request.POST['data'])
        sm = ShippingMethod.objects.get(id=data['shippingMethod'])
        if sm.needsShipping:
            if 'receiver' in data:
                receiver = ShippingForm(data['receiver'])
                if receiver.is_valid():
                    pass
                else:
                    hasErrors = True
            if 'buyer' in data:
                buyer = ShippingForm(data['buyer'])
                if buyer.is_valid():
                    pass
                else:
                    hasErrors = True
        if data['hasInvoice']:
            invoice = InvoiceForm(data['invoice'])
            if invoice.is_valid():
                pass
            else:
                hasErrors = True
        else:
            invoice = InvoiceForm()

        if not hasErrors:
            pm = PaymentMethod.objects.get(id=data['paymentMethod'])
            c = Cart.objects.get(id=request.session['cartId'])
            if pm.needsProcessing:
                [status, message] = processOrder(data)
                if not status:
                    return HttpResponse(json.dumps({'success': status, 'message': message}))
                else:
                    order = Order(paymentMethod=pm, shippingMethod=sm, cart=c,
                                  date=datetime.datetime.now(), notes=data['notes'], status='PENDING')
                    order.save()

            order = Order(paymentMethod=pm, shippingMethod=sm, cart = c, email = data['email'],
                          date=datetime.datetime.now(), notes=data['notes'], status='PENDING')
            order.save()
            c.json = CartSerializer(c).data
            #c.order = order
            c.save()

            if request.user.is_authenticated():
                order.user = request.user
                if order.shippingMethod.needsShipping:
                    receiver = receiver.save(commit=False)
                    receiver.user = request.user
                    buyer = buyer.save(commit=False)
                    buyer.user = request.user
            order.email = data['buyerEmail']
            if order.shippingMethod.needsShipping:
                buyer.order = order
                buyer.type = 'BU'
                buyer.save()
                receiver.type = 'RE'
                receiver.order = order
                receiver.save()
            order.save()


            #wysyłanie emaili
            newOrder(order, request)

            del request.session['cartId']
            return HttpResponse(json.dumps({'success': True, 'message': pm.instructions}))

    else:
        if request.user.is_authenticated():
            try:
                invoice = InvoiceForm(instance=Invoice.objects.get(user=request.user))
            except:
                invoice = InvoiceForm()
        else:
            invoice = InvoiceForm()
    try:
        products_in_cart = CartProduct.objects.filter(cart__id = request.session['cartId']).count()
    except:
        products_in_cart = 0
    creationForm = UserCreationForm()
    shippingMethods = ShippingMethod.objects.all()

    try:
        receiver
    except:
        if request.user.is_authenticated():
            try:
                receiver = ShippingForm(instance=Shipment.objects.get(user=request.user,type='RE'))
            except:
                receiver = ShippingForm()
            try:
                buyer = ShippingForm(instance=Shipment.objects.get(user=request.user,type='BU'))
            except:
                buyer = ShippingForm()
        else:
            receiver = ShippingForm()
            buyer = ShippingForm()

    return render_to_response('checkout.djhtml',
                              {'BuyerForm': buyer, 'ReceiverForm': receiver, 'creationForm': creationForm,
                              'ShippingMethods': shippingMethods, 'InvoiceForm': invoice,
                              'products_in_cart': products_in_cart, 'step': request.user.is_authenticated() if 2 else 1,
                              'shippingMethod': data['shippingMethod'] if 'data' in request.POST else 0,
                              'paymentMethod': data['paymentMethod'] if 'data' in request.POST else 0,
                              'email': data['email'] if 'data' in request.POST else '' },
                              context_instance=RequestContext(request))

def getOrderOptions(request):
    try:
        cart = Cart.objects.get(id=request.session['cartId'])
    except:
        return HttpResponse(json.dumps({'success': False}))
    totals = {}
    totals['products'] = cart.getTotal()
    try:
        sm = ShippingMethod.objects.get(id=request.GET['shipping'])
        totals['shipping'] = sm.price
        paymentMethods = PaymentMethod.objects.filter(shippingMethods=sm)
        needsShipping = sm.needsShipping
    except:
        totals['shipping'] = ShippingMethod.objects.first().price
        paymentMethods = PaymentMethod.objects.all()
        needsShipping = False
    totals['total'] = totals['products'] + totals['shipping']
    shippingMethods = ShippingMethodSerializer(ShippingMethod.objects.all(), many=True).data
    paymentMethods = PaymentMethodSerializer(paymentMethods, many=True).data

    return HttpResponse(json.dumps({'success': True, 'totals': totals, 'shippingMethods': shippingMethods,
                                    'paymentMethods': paymentMethods,
                                    'needsShipping': needsShipping}))


@csrf_exempt
def loginView(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        # the password verified for the user
        if user.is_active:
            login(request, user)
            if 'source' in request.POST:
                return HttpResponseRedirect(request.POST['source'])
            else:
                return HttpResponse(json.dumps({'success': True}))
        else:
            if 'source' in request.POST:
                return HttpResponseRedirect(request.POST['source'])
            else:
                return HttpResponse(json.dumps({'success': False,
                                                'message': "The password is valid, but the account has been disabled!"}))
    else:
        # the authentication system was unable to verify the username and password
        return HttpResponse(json.dumps({'success': False, 'message': "The username and password were incorrect."}))


# class CartProductsList(APIView):
# """
#     List all snippets, or create a new snippet.
#     """
#     def get(self, request, format=None):
#         cartProducts = ProductCart.objects.all()
#         serializer = CartProductSerializer(cartProducts, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#         serializer = CartProductSerializer(data=request.DATA)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def removeFromCart(request):
    id = request.GET['product']
    CartProduct.objects.get(id = id).delete()
    return HttpResponse(json.dumps({'success': True}))

def updateCart(request):
    id = request.GET['product']
    quantity = request.GET['quantity']
    cp = CartProduct.objects.get(id = id)
    cp.quantity = quantity
    cp.save()
    return HttpResponse(json.dumps({'success': True}))

def addToCart(request):
    if 'quantity' in request.POST:
        quantity = request.POST['quantity']
    else:
        quantity = 1
    if 'product' in request.POST or 'productVariation' in request.POST:
        if not 'cartId' in request.session or request.session['cartId'] == None:
            c = Cart()
            c.save()
            request.session['cartId'] = c.id
        else:
            c = Cart.objects.get(id=request.session['cartId'])
        if 'product' in request.POST:
            p = Product.objects.get(id=request.POST['product'])
            cp = CartProduct(product=p, cart=c, price=p.price, quantity=quantity)
        else:
            pv = ProductVariation.objects.get(id=request.POST['productVariation'])
            cp = CartProduct(productVariation=pv, cart=c, price=pv.price,
                             quantity=quantity)
        cp.save()
        return HttpResponse(json.dumps({'success': True}))
    else:
        return HttpResponse(json.dumps({'success': False}))


class IntegerListFilter(django_filters.Filter):
    def filter(self, qs, value):
        if value not in (None, ''):
            integers = [int(v) for v in value.split(',')]
            return qs.filter(**{'%s__%s' % (self.name, self.lookup_type): integers})
        return qs


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(name="price", lookup_type='gte')
    max_price = django_filters.NumberFilter(name="price", lookup_type='lte')
    categories_in = IntegerListFilter(name='categories__id', lookup_type='in')
    attributes_in = IntegerListFilter(name='attributes__id', lookup_type='in')

    class Meta:
        model = Product
        fields = ('id', 'min_price', 'max_price', 'categories_in', 'attributes_in')


class ProductListView(generics.ListAPIView):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_class = ProductFilter
    paginate_by = 9


@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            if 'source' in request.POST:
                return HttpResponseRedirect("/" + request.POST['source'] + "/")
            else:
                return HttpResponseRedirect("/register/")
    else:
        form = UserCreationForm()
    if 'source' in request.POST and request.POST['source'] == 'checkout':
         return render_to_response('checkout.djhtml', {'creationForm': form,
                                                       'products_in_cart': True}, context_instance=RequestContext(request))
    else:
        return render(request, "registerView.html", {
            'form': form,
        })


def logoutView(request):
    logout(request)
    url = request.META['HTTP_REFERER'].split('/')[-1]
    return HttpResponseRedirect('/' + url)


def singleProduct(request, name):
    product = Product.objects.get(name=name)
    return render_to_response('singleProduct.djhtml', {'product': product}, context_instance=RequestContext(request))


def quickContact(request):
    qc = QuickContactForm(request.POST)
    if qc.is_valid():
        send_mail('Wiadomość kontaktowa', request.POST['body'], request.POST['email'],
                  'oleje.amsoil@gmail.com', fail_silently=False)
    else:
        return render_to_response('index.djhtml', {}, context_instance=RequestContext(request))

def search(request):
    term = request.GET['term']
    pages = Page.objects.filter(Q(body__contains=term) | Q(title__contains=term))
    products = Product.objects.filter(Q(name__contains=term) | Q(description__contains=term))
    res = []
    for p in pages:
        res.append( { 'id':p.id, 'except': p.body[0:200], 'title':p.title, 'link' : '/page/'+p.name } )
    for p in products:
        res.append( { 'id':p.id, 'except': p.shortDescription[0:200], 'title':p.name, 'link' : '/shop/'+p.name+'/' } )
    return render_to_response('search.html', {'results': res, 'count': len(res)}, context_instance=RequestContext(request))