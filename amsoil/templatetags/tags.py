#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import template
from amsoil.models import MenuItem, Category, CartProduct, Cart, Invoice, Shipment, Order, Slider, Slide, \
    Attribute, AttributeGroup, ProductVariation, UserMeta, Product, Template
from amsoil.models import getProductAttributesByGroupName
from django.db.models import Sum, Count, Min, Max
from amsoil.forms import QuickContactForm
from django.utils.translation import ugettext as _
from shop.settings import MEDIA_URL
from amsoil.forms import ShippingForm
from django.shortcuts import RequestContext, render_to_response, redirect
from django.core.mail import send_mail
from django import template
from django.template import RequestContext
from django.template import Template as D_template

register = template.Library()


@register.filter
def join_by_attr(the_list, attr_name, separator=', '):
    return separator.join(unicode(getattr(i, attr_name)) for i in the_list)

def is_shop_limited(context):
    params = {}
    keys = ['atrybuty','kategorie']
    urls = context['request'].path.split('/')
    for k in keys:
        try:
            ind = urls.index(k)
            params[k] = urls[ind + 1].split(',')
        except:
            pass
        try:
            ind = context.dicts[1][k]
            params[k] = ind
        except:
            pass

    if len(params) > 0:
        return get_products_query_set(params)
    else:
        return False


@register.inclusion_tag('tags/display_form.html', takes_context=True)
def display_form(context, form=None, success=None, message=None):
    exec 'from amsoil.forms import %s as FormClass' % form
    request = context['request']
    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            if send_mail('Prośba o dobór produktów', 'Prośba o dobór produktów', request.POST['email'],
                         ['info@najlepszysyntetyk.pl'], fail_silently=False, html_message=form.as_table()):
                message = '<h2>Dziękujemy</h2><p>Twoje zapytanie zostało przesłane</p>'
            else:
                message = '<h2>Błąd</h2><p>Przesłanie formularza nie powiodło się</p>'
    else:
        form = FormClass()
    return {'form': form, 'success': success, 'action': request.path, 'message': message}


@register.inclusion_tag('tags/template.html', takes_context=True)
def display_template(context, name):
    try:
        tem = Template.objects.get(name=name)
        text = render_tags(context, tem.body.rendered)['val']
    except:
        tem = False
    return {'template': text if tem else ''}


@register.inclusion_tag('tags/discount_info.html', takes_context=True)
def discount_info(context):
    request = context['request']
    if UserMeta.getValue(request.user, 'discount'):
        return {
            'discount': {'ends': UserMeta.getValue(request.user, 'discount_ends'),
                         'size': UserMeta.getValue(request.user, 'discount')}
        }
    else:
        return {'discount': False}


@register.inclusion_tag('special_shop.html', takes_context=True)
def special_shop(context, *args, **kwargs):
    categories_names = kwargs['kategorie'].encode('utf8').split(',') if 'kategorie' in kwargs else ''
    attributes_names = kwargs['atrybuty'].encode('utf8').split(',') if 'atrybuty' in kwargs else ''
    attributes = Attribute.objects.filter(name__in=attributes_names)
    categories = Category.objects.filter(name__in=categories_names)
    attributes_ids = [str(a.id) for a in attributes]
    categories_ids = [str(c.id) for c in categories]

    return {
        'filtry': kwargs['filtry'].encode('utf8').split(',') if 'filtry' in kwargs else [],
        'atrybuty': attributes_names,
        'kategorie': categories_names,
        'category_id':  ','.join(categories_ids) if len(categories_ids) > 0 else -1,
        'attributes_id':  ','.join(attributes_ids) if len(attributes_ids) > 0 else -1,
        'request': context['request']
    }


@register.inclusion_tag('render_tags.html', takes_context=True)
def render_tags(context, value):
    t = D_template('{%load tags%}{%load i18n%}' + value)
    c = RequestContext(context['request'])
    return {'val': t.render(c)}


@register.inclusion_tag('promoDiv.html')
def promoDiv(content, color=None, background=None, icon=None, image=None, size=None, url=None):
    return {
        'color': color,
        'background': background,
        'content': content,
        'icon': icon,
        'image': image,
        'size': size,
        'url': url,
    }


@register.filter(is_safe=True, needs_autoescape=False)
def currency(value, show_currency=True):
    # return '<span class="currency">PLN</span><span class="item-price">'+str(value)+'</span>'
    if show_currency:
        return ("%.2f" % float(value)).replace('.',',') + ' zł'
    else:
        return ("%.2f" % float(value)).replace('.',',')


def placeholder(value):
    value.field.widget.attrs["placeholder"] = value.help_text
    return value


register.filter(placeholder)


@register.inclusion_tag('sorter.html')
def sorter():
    return {
    }


@register.inclusion_tag('priceFilter.html', takes_context=True)
def priceFilter(context, *args, **kwargs):
    products = is_shop_limited(context)
    if products:
        pvs = ProductVariation.objects.filter(product__in=products)
    else:
        pvs = ProductVariation.objects.all()
    minimum = int(pvs.aggregate(Min('price')).values()[0])
    maximum = int(pvs.aggregate(Max('price')).values()[0])
    return {
        'min': minimum,
        'max': maximum
    }


@register.inclusion_tag('productsTabs.html')
def productsTabs():
    newest = ProductVariation.objects.all().order_by('added_date')[0:4]
    best = ProductVariation.objects.all().order_by('-total_sales')[0:4]
    promo = ProductVariation.objects.filter(product__categories__name='promotion')[0:4]
    return {
        'cats': [
            {'name': 'Nowości', 'id': 'newest', 'products': newest, 'first': True,
             'width': 3},
            {'name': 'Bestsellery', 'id': 'best', 'products': best,
             'width': 3},
            {'name': 'Promocje', 'id': 'promo', 'products': promo,
             'width': 3}
        ]
    }


@register.inclusion_tag('nav.djhtml')
def nav(name=None):
    mi = MenuItem.objects.filter(menu__name='main').order_by('order')
    lp = getProductAttributesByGroupName('Lepkość')
    pr = getProductAttributesByGroupName('Marka')
    return {
        'brands': pr,
        'vis': lp,
        'categories': Category.objects.filter(forProducts=True),
        'menuItems': mi,
        'count': mi.count() + 2,
        'offset': mi.count() + 2
    }


@register.inclusion_tag('productCategories.djhtml', takes_context=True)
def productCategories(context, name=None, *args, **kwargs):
    products = is_shop_limited(context)
    if products:
        categories = Category.objects.filter(forProducts=True, pages__in=products).annotate(dcount=Count('pages__id')).order_by('order')
    else:
        categories = Category.objects.filter(forProducts=True).annotate(dcount=Count('pages__id')).order_by('order')
    return {
        'asLink': 'asLink' in kwargs if True else False,
        'categories': categories,
    }


@register.inclusion_tag('productFilter.html', takes_context=True)
def productFilter(context, type=None, *args):
    products = is_shop_limited(context)
    if products:
        # options = Attribute.objects.filter(group__name=type, pages__isnull=False, products__in = products).\
        #    annotate(dcount=Count('id'))
        options = Attribute.objects.filter(group__name=type, pages__in=products).annotate(dcount=Count('pages__id'))
    else:
        options = Attribute.objects.filter(group__name=type, pages__isnull=False).annotate(dcount=Count('pages__id'))
    return {
        'options': options,
        'type': type
    }


@register.inclusion_tag('minicart.djhtml', takes_context=True)
def cartData(context, *args, **kwargs):
    request = context['request']
    if 'noButtons' in kwargs:
        noButtons = True
    else:
        noButtons = False
    if 'cartId' in request.session:
        items = CartProduct.objects.filter(cart__id=request.session['cartId'])
        return {
            'noButtons': noButtons,
            'items': items,
            'total': items.aggregate(
                total=Sum('price', field="price*quantity"))['total'],
            'count': items.aggregate(Sum('quantity')).values()[0]
        }
    else:
        return {
            'items': [],
            'total': 0,
            'count': 0,
        }


@register.inclusion_tag('addresses.html', takes_context=True)
def addresses(context, order, *args, **kwargs):
    try:
        receiver = ShippingForm(instance=Shipment.objects.get(order=order, type='RE'))
    except:
        receiver = False
    try:
        buyer = ShippingForm(instance=Shipment.objects.get(order=order, type='BU'))
    except:
        buyer = False
    return {
        'buyer': buyer,
        'receiver': receiver
    }


@register.inclusion_tag('cart.djhtml', takes_context=True)
def cartItems(context, order=False, *args, **kwargs):
    request = context['request']
    if 'cart' in kwargs:
        cartId = kwargs['cart'].id
    elif 'orderId' in kwargs:
        order = Order.objects.get(id=kwargs['orderId'])
        cartId = order.cart.id
    elif 'cartId' in request.session:
        cartId = request.session['cartId']
    else:
        cartId = None
    if cartId:
        cart = Cart.objects.get(id=cartId)
        items = CartProduct.objects.filter(cart=cart)
        total = cart.getTotal()
        discount = cart.getDiscount(request.user)
        if discount:
            total -= discount
        if order:
            total = total + order.shippingMethod.price
        return {
            'discount': discount,
            'withCheckoutButton': 'withCheckoutButton' in kwargs,
            'noButtons': True if 'noButtons' in kwargs else False,
            'items': items,
            'total': str(total),
            'count': items.aggregate(Sum('quantity')).values()[0],
            'order': order
        }
    else:
        return {
            'discount': False,
            'items': [],
            'total': 0,
            'count': 0,
        }


@register.inclusion_tag('breadcrumbs.html', takes_context=True)
def breadcrumbs(context):
    res = [{'url': '/', 'name': _('home')}]
    els = context['request'].path.split('/')
    i = 1
    for e in els:
        if len(e) > 0:
            if e not in ['produkt', 'category', 'atrybuty', 'kategorie']:
                res.append({'url': '/'.join(els[0:i]), 'name': e})
        i = i + 1
    res[-1]['last'] = True
    return {
        'crumbs': res
    }


@register.inclusion_tag('quickContact.html', takes_context=True)
def quickContact(context):
    request = context['request']
    if request.POST:
        form = QuickContactForm(request.POST)
    else:
        form = QuickContactForm()
    return {
        'form': form
    }


@register.inclusion_tag('slider.html')
def slider(*args, **kwargs):
    slider = Slider.objects.get(name=kwargs['name'])
    return {
        'root': MEDIA_URL,
        'slider': slider,
        'slides': Slide.objects.filter(slider=slider).order_by('order')
    }


def get_products_query_set(params):
    pr = Product.objects.all()
    if 'atrybuty' in params and len(params['atrybuty']) > 0:
        pr = Product.objects.filter(attributes__name__in=params['atrybuty'])
    if 'kategorie' in params and len(params['kategorie']) > 0:
        pr = pr & Product.objects.filter(categories__name__in=params['kategorie'])
    return pr
