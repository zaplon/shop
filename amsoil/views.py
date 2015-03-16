#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, RequestContext, HttpResponse, HttpResponseRedirect, render
from amsoil.models import Page, Product, Cart, User, CartProduct, ProductVariation, Post,\
    ShippingMethod, PaymentMethod, Order, Invoice, Shipment, Category, Attribute, UserMeta, NewsletterReceiver
from rest_framework import viewsets
from amsoil.serializers import ProductSerializer, PaymentMethodSerializer, ShippingMethodSerializer, \
    CartSerializer, CartProductSerializer, NewsletterReceiverSerializer, ProductVariationSerializer,\
    ShopProductSerializer, OrderSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import django_filters, json, datetime, simplejson
from amsoil.forms import ShippingForm, InvoiceForm, QuickContactForm, CheckoutBasicForm, UserEditForm
from authentication.admin import UserCreationForm
from amsoil.templatetags.tags import currency

from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum
from django.core import serializers
from django.core.mail import send_mail
from django.db.models import Q
from shop.settings import CHECKOUT_THANK_YOU, CHECKOUT_FAILED

from amsoil.mails import newOrder, orderNotification
from authentication.admin import UserCreationForm

from getpaid.forms import PaymentMethodForm
from getpaid.views import NewPaymentView

from django.views.generic.detail import DetailView
from getpaid.forms import PaymentMethodForm
from .models import Order




class OrderView(DetailView):
    model=Order

    def get_context_data(self, **kwargs):
        context = super(OrderView, self).get_context_data(**kwargs)
        context['payment_form'] = PaymentMethodForm("PLN", initial={'order': Order})
        return context

def home(request):
    return render_to_response('index.djhtml', {}, context_instance=RequestContext(request))


def page(request, title):
    try:
        page = Page.objects.get(title=title)
    except:
        page = Page.objects.get(url=title)
    return render_to_response('page.html', {'page': page}, context_instance=RequestContext(request))


def shop(request):
    path = request.path.split('/')

    attributes_id = -1
    try:
        attributes_id = []
        att_ind = path.index('atrybuty')
        atts = path[att_ind + 1].split(',')
        for a in atts:
            attributes_id.append(Attribute.objects.get(name=path[att_ind + 1]).id)
        attributes_id = ','.join(map(str, attributes_id))
    except:
        attributes_id = -1

    category_id = -1
    try:
        cat_ind = path.index('kategorie')
        category_id = Category.objects.get(name=path[cat_ind + 1]).id
        # return render_to_response('shop.djhtml', {'category_id': category_id}, context_instance=RequestContext(request))
    except:
        pass
    return render_to_response('shop.djhtml', {'category_id': category_id, 'attributes_id': attributes_id},
                              context_instance=RequestContext(request))


def cart(request):
    return render_to_response('cartView.html', [], context_instance=RequestContext(request))


def account(request):
    us = request.user
    try:
        invoice = InvoiceForm(instance=Invoice.objects.get(user=us))
    except:
        invoice = InvoiceForm()
    try:
        payer = ShippingForm(instance=Shipment.objects.get(user=us, type='BU'))
    except:
        payer = ShippingForm()
    try:
        shipment = ShippingForm(instance=Shipment.objects.get(user=us, type='RE'))
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
                pay.type = 'BU'
                pay.save()
        if request.POST['type'] == 'shipment':
            shipment = ShippingForm(request.POST)
            if shipment.is_valid():
                shi = shipment.save(commit=False)
                shi.type = 'RE'
                shi.user = us
                shi.save()

        if request.POST['type'] == 'user':
            userForm = UserEditForm(request.POST)
            if userForm.is_valid():
                uf = userForm.save(commit=False)
                uf.save()

    if request.user.is_authenticated():
        orders = Order.objects.filter(user=request.user)
    else:
        orders = []

    return render_to_response('myAccount.html', {
        'userChangeForm': UserEditForm(instance=us),
        'invoiceForm': invoice,
        'shipmentForm': shipment,
        'payerForm': payer,
        'orders': orders,
    }, context_instance=RequestContext(request))


def processOrder(order, request):
    if order.paymentMethod.code == 'pp':
        pass
    else:
        pmf = PaymentMethodForm(currency='PLN', data={'order': order.id, 'backend':'getpaid.backends.transferuj'})
        if pmf.is_valid():
            npv = NewPaymentView()
            npv.request = request
            return npv.form_valid(pmf)




def takeCart(request):
    cart = Cart.objects.get(id=request.POST['id'])
    request.session['cartId'] = cart.id
    return HttpResponse(json.dumps({'success': True}))


def minicart(request):
    if 'cartId' in request.session:
        items = CartProduct.objects.filter(cart__id=request.session['cartId'])
        return HttpResponse(json.dumps({
            'items': CartProductSerializer(items, many=True).data,
            'total': str(items.aggregate(
                total=Sum('price', field="price*quantity"))['total']) + 'zł',
            'count': items.aggregate(Sum('quantity')).values()[0]
        }))
    else:
        return HttpResponse(json.dumps({
            'items': [],
            'total': 0,
            'count': 0,
        }))


def checkout_failure(request,pk):
    order = Order.objects.get(id=id)
    order.status = 'FAILED'
    order.save()
    msg = CHECKOUT_FAILED
    return render_to_response('checkout_success.html', {'message':msg})


def checkout_processed(request,pk):
    order = Order.objects.get(id=pk)
    order.status = 'FINISHED'
    order.save()
    msg = CHECKOUT_THANK_YOU
    return render_to_response('checkout_success.html', {'message':msg})


def checkout(request):

    #potwierdzenie z paypal
    # if request.method == 'GET' and 'paymentId' in request.GET:
    #     order = paypal_step_2(request)
    #     if not order:
    #         return render_to_response('checkout_success.html', {'message':CHECKOUT_FAILED})
    #     order.save()
    #     msg = CHECKOUT_THANK_YOU
    #     return render_to_response('checkout_success.html', {'message':msg})

    if request.method == 'POST':
        hasErrors = False
        data = json.loads(request.POST['data'])
        sm = ShippingMethod.objects.get(id=data['shippingMethod'])

        basics = CheckoutBasicForm(data['checkoutBasic'])
        if not basics.is_valid():
            hasErrors = True

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
            processed = False

            order = Order(paymentMethod=pm, shippingMethod=sm, cart=c, email=basics.cleaned_data['email'],
                              phone=basics.cleaned_data['tel'], date=datetime.datetime.now(), notes=data['notes'],
                              status='PENDING')


            order.total = order.cart.getTotal()
            #znizki
            if request.user.is_authenticated():
                now_date=datetime.datetime.now()
                next_year = now_date + datetime.timedelta(days=365)

                last_12_months = Order.objects.filter(user=request.user,date__gte=now_date-datetime.timedelta(days=365)).\
                    aggregate(Sum('total')).values()[0]
                if last_12_months > 1000:
                    UserMeta.setValue(request.user,'discount','20')
                    UserMeta.setValue(request.user,'discount_ends',next_year.strftime('%Y-%m-%d'))
                elif last_12_months > 500:
                    UserMeta.setValue(request.user,'discount','15')
                    UserMeta.setValue(request.user,'discount_ends',next_year.strftime('%Y-%m-%d'))
                elif last_12_months > 300:
                    UserMeta.setValue(request.user,'discount','10')
                    UserMeta.setValue(request.user,'discount_ends',next_year.strftime('%Y-%m-%d'))

                if UserMeta.getValue(request.user,'discount'):
                    end_date = datetime.datetime.strptime(UserMeta.getValue(request.user,'discount_ends'),'%Y-%m-%d')
                    if end_date > now_date:
                        order.total = order.total - order.total * float(UserMeta.getValue(request.user,'discount'))/100

            order.total += order.paymentMethod.price + order.shippingMethod.price

            if pm.needsProcessing:
                order.save()
                res = processOrder(order,request)
                return HttpResponse(json.dumps( {'success': True, 'url': res.url } ))
            c.json = CartSerializer(c).data
            # c.order = order
            c.save()

            order.save()

            #pierwsze i ostanie zapisanie faktury
            if data['hasInvoice']:
                invoice.order = order
                invoice.save()

            #zapisywanie adresów
            if order.shippingMethod.needsShipping:
                buyer = buyer.save(commit=False)
                if 'receiver' in data:
                    receiver = receiver.save(commit=False)

            #if request.user.is_authenticated():
            #    order.user = request.user
            #    if order.shippingMethod.needsShipping:
            #        if 'receiver' in data:
            #            receiver.user = request.user
            #        buyer.user = request.user


            if order.shippingMethod.needsShipping:
                buyer.type = 'BU'
                buyer.order = order
                if 'receiver' in data:
                    receiver.type = 'RE'
                    receiver.order = order
                buyer.save()
                if 'receiver' in data:
                    receiver.save()

            order.save()

            #zmniejszamy stany magazynowe
            for cp in order.cart.cartProducts.all():
                pv = cp.productVariation
                pv.amount -= 1
                pv.total_sales += 1
                pv.save()


            #wysyłanie emaili
            newOrder(order, request)
            orderNotification(order, request)

            del request.session['cartId']
            thanks_message = CHECKOUT_THANK_YOU
            return HttpResponse(json.dumps({'success': True, 'message': thanks_message+pm.instructions.encode('utf8')}))

    else:
        if request.user.is_authenticated():
            try:
                invoice = InvoiceForm(instance=Invoice.objects.get(user=request.user))
            except:
                invoice = InvoiceForm()
        else:
            invoice = InvoiceForm()

        if request.user.is_authenticated():
            basics = CheckoutBasicForm(initial={'email': request.user.email})
        else:
            basics = CheckoutBasicForm()
    try:
        products_in_cart = CartProduct.objects.filter(cart__id=request.session['cartId']).count()
    except:
        products_in_cart = 0
    creationForm = UserCreationForm()
    shippingMethods = ShippingMethod.objects.all()

    try:
        receiver
    except:
        if request.user.is_authenticated():
            try:
                receiver = ShippingForm(instance=Shipment.objects.get(user=request.user, type='RE'))
            except:
                receiver = ShippingForm()
        else:
            receiver = ShippingForm()

        # jeżeli z jakiś przyczyn tego nie ma wcześniej
        try:
            buyer
        except:
            if request.user.is_authenticated():
                try:
                    buyer = ShippingForm(instance=Shipment.objects.get(user=request.user, type='BU'))
                except:
                    buyer = ShippingForm()
            else:
                buyer = ShippingForm()

    try:
        data
    except:
        data = {}
    return render_to_response('checkout.djhtml',
                              {'BuyerForm': buyer, 'ReceiverForm': receiver, 'creationForm': creationForm,
                               'ShippingMethods': shippingMethods, 'InvoiceForm': invoice,
                               'CheckoutBasicForm': basics,
                               'notes':  data['notes'] if 'notes' in data else False,
                               'hasInvoice': True if 'hasInvoice' in data and data['hasInvoice']==True else False,
                               'buyerAsReceiver': True if not 'receiver' in data else False,
                               'products_in_cart': products_in_cart,
                               'shippingMethod': data['shippingMethod'] if 'data' in request.POST else 0,
                               'paymentMethod': data['paymentMethod'] if 'data' in request.POST else 0,
                               'step': 3 if 'data' in request.POST else 2 if request.user.is_authenticated() else 1,
                               'terms': True if 'terms' in data and data['terms'] == True else False,
                              },
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
    totals['discount'] = cart.getDiscount(request.user)
    totals['total'] = currency(totals['products'] + totals['shipping'] - totals['discount'])
    totals['shipping'] = currency(totals['shipping'])
    totals['discount'] = currency(totals['discount'])
    totals['products'] = currency(totals['products'])
    shippingMethods = ShippingMethodSerializer(ShippingMethod.objects.all(), many=True).data
    paymentMethods = PaymentMethodSerializer(paymentMethods, many=True).data

    return HttpResponse(json.dumps({'success': True, 'totals': totals, 'shippingMethods': shippingMethods,
                                    'paymentMethods': paymentMethods,
                                    'needsShipping': needsShipping}))


# class CartProductsList(APIView):
# """
# List all snippets, or create a new snippet.
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
    CartProduct.objects.get(id=id).delete()
    return HttpResponse(json.dumps({'success': True}))


def updateCart(request):
    id = request.GET['product']
    quantity = request.GET['quantity']
    cp = CartProduct.objects.get(id=id)
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
            pv = p.variations.first()
            cp = CartProduct(productVariation=pv, cart=c, price=pv.price, quantity=quantity)
        else:
            pv = ProductVariation.objects.get(id=request.POST['productVariation'])
            if pv.amount < int(quantity):
                return HttpResponse(json.dumps({'success': False}))
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

class GeekRangeFilter(django_filters.Filter):
    def filter(self, qs, value):
        if value not in (None, ''):
            integers = [int(v) for v in value.split(',')]
            return qs.filter(**{'%s__%s' % (self.name, self.lookup_type): integers}).distinct()
        return qs

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(name="variations__price", lookup_type='gte')
    max_price = django_filters.NumberFilter(name="variations__price", lookup_type='lte')
    categories_in = IntegerListFilter(name='categories__id', lookup_type='in')
    attributes_in = IntegerListFilter(name='attributes__id', lookup_type='in')
    price_in = GeekRangeFilter(name='variations__price', lookup_type='range')
    #price_in = django_filters.RangeFilter(name='variations__price', distinct=True)

    def get_order_by(self, order_value):
        return [order_value]
    class Meta:
        model = Product
        distinct = True
        order_by = ['name','-name','variations__added_date','variations__price','-variations__added_date','-variations__price']
        fields = ('id', 'min_price', 'max_price', 'categories_in', 'attributes_in','price_in',
                  'variations__added_date','variations__price','attributes__id','categories__id')



class NewsletterReceiverListCreateView(generics.ListCreateAPIView):
    queryset = NewsletterReceiver.objects.all()
    serializer_class = NewsletterReceiverSerializer


def postsView(request):
    posts = Post.objects.all().order_by('-created_at')
    return render_to_response('posts.html', {'posts': posts}, context_instance=RequestContext(request))


def postView(request, url):
    post = Post.objects.get(url=url)
    return render_to_response('post.html', {'post': post}, context_instance=RequestContext(request))


class ProductListView(generics.ListAPIView):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_class = ProductFilter
    paginate_by = 9


class ShopProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_published=True)
    serializer_class = ShopProductSerializer
    filter_class = ProductFilter
    paginate_by = 9
    def get(self, request, format=None):
        try:
            cId = Category.objects.get(name='Promocje').id
        except:
            cId = 0
        list = self.list(request)
        for p in list.data['results']:
            p['grouped_variations'] = simplejson.loads(p['grouped_variations'].replace("'",'"'),'utf-8')
            p['min_price'] = min(p['variations'], key=lambda x: x['price'])['price']
            p['on_promotion'] = cId in p['categories']
        return list

def singleProduct(request, name):
    product = Product.objects.get(name=name)
    return render_to_response('singleProduct.djhtml', {'product': product}, context_instance=RequestContext(request))


def quickContact(request):
    qc = QuickContactForm(request.POST)
    if qc.is_valid():
        if send_mail('Wiadomość kontaktowa', request.POST['body'], request.POST['email'],
                  ['oleje.amsoil@gmail.com'], fail_silently=False):
            return render_to_response('index.djhtml',
                                      {'message':'Wiadomość wysłana','message_icon':'glyphicon glyphicon-ok'},
                                      context_instance=RequestContext(request))
        else:
            return render_to_response('index.djhtml',
                                      {'message':'Wystąpił błąd podczas wysyłania wiadomości',
                                       'message_icon':'glyphicon glyphicon-remove'},
                                      context_instance=RequestContext(request))

    else:
        return render_to_response('index.djhtml', {}, context_instance=RequestContext(request))


def search(request):
    term = request.GET['term']
    pages = Page.objects.filter(Q(body__icontains=term) | Q(title__icontains=term))
    products = Product.objects.filter(Q(name__icontains=term) | Q(description__icontains=term))
    res = []
    for p in pages:
        res.append({'id': p.id, 'except': p.body[0:200], 'title': p.title, 'link': '/' + p.url})
    for p in products:
        res.append({'id': p.id, 'except': p.shortDescription[0:200], 'title': p.name, 'link': '/sklep/produkt/' + p.name + '/'})
    return render_to_response('search.html', {'results': res, 'count': len(res)},
                              context_instance=RequestContext(request))


class ProductVariationViewSet(viewsets.ModelViewSet):
    queryset = ProductVariation.objects.all()
    serializer_class = ProductVariationSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

def form_submitted(request):
    return render_to_response('form_submitted.html', {}, context_instance=RequestContext(request))