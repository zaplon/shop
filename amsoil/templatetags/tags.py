#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import template
from amsoil.models import MenuItem, Category, CartProduct, Cart, Invoice, Shipment, Order, Slider, Slide, \
    Attribute, AttributeGroup, ProductVariation, UserMeta
from amsoil.models import getProductAttributesByGroupName
from django.db.models import Sum, Count, Min, Max
from amsoil.forms import QuickContactForm
from django.utils.translation import ugettext as _
from shop.settings import MEDIA_URL


from django import template
from django.template import RequestContext
from django.template import Template

register = template.Library()

@register.inclusion_tag('render_tags.html',takes_context=True)
def render_tags(context,value):
    t = Template( '{%load tags%}' + value)
    c = RequestContext(context['request'])
    return  { 'val':t.render(c) }

@register.inclusion_tag('promoDiv.html')
def promoDiv(content, color=None, background=None, icon=None, image=None, size=None):
    return {
        'color': color,
        'background': background,
        'content': content,
        'icon': icon,
        'image': image,
        'size': size
    }

@register.filter(is_safe=True,needs_autoescape=False)
def currency(value):
	#return '<span class="currency">PLN</span><span class="item-price">'+str(value)+'</span>'
	return 'PLN' + str(value)
	
def placeholder(value):
	value.field.widget.attrs["placeholder"] = value.help_text
	return value

register.filter(placeholder)


@register.inclusion_tag('priceFilter.html')
def priceFilter():
    pvs = ProductVariation.objects.all()
    minimum = pvs.aggregate(Min('price'))
    maximum = pvs.aggregate(Max('price'))
    return {
    	'min': minimum,
    	'max': maximum
    }

@register.inclusion_tag('productsTabs.html')
def productsTabs():
    newest = ProductVariation.objects.all().order_by('added_date')[0:4]
    best = ProductVariation.objects.all().order_by('total_sales')[0:4]
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
    pr = getProductAttributesByGroupName('Producent')
    return {
        'brands': pr,
        'vis': lp,
        'categories': Category.objects.filter(forProducts=True),
        'menuItems': mi,
        'count': mi.count() + 2,
        'offset': mi.count() + 2
    }


@register.inclusion_tag('productCategories.djhtml')
def productCategories(name=None, *args, **kwargs):
    return {
        'asLink': 'asLink' in kwargs if True else False,
        'categories': Category.objects.filter(forProducts=True),
    }


@register.inclusion_tag('productFilter.html')
def productFilter(type=None, *args):
    options = Attribute.objects.filter(group__name=type, pages__isnull=False).annotate(dcount=Count('id'))
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


@register.inclusion_tag('cart.djhtml', takes_context=True)
def cartItems(context, *args, **kwargs):
    request = context['request']
    if 'orderId' in kwargs:
        cartId = Order.objects.get(id=kwargs['orderId']).cart.id
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
        return {
            'discount': discount,
            'noButtons': True if 'noButtons' in kwargs else False,
            'items': items,
            'total': str(total),
            'count': items.aggregate(Sum('quantity')).values()[0]
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
            if e != 'product' and e != 'category':
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
        'slides': Slide.objects.filter(slider=slider)
    }
