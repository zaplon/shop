#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import template
from amsoil.models import MenuItem, Category, CartProduct, Cart, Invoice, Shipment, Order, Slider, Slide
from django.db.models import Sum
from amsoil.forms import QuickContactForm
from django.utils.translation import ugettext as _
from shop.settings import MEDIA_URL


register = template.Library()

@register.inclusion_tag('nav.djhtml')
def nav(name=None):
    mi = MenuItem.objects.filter(menu__name='main').order_by('order')
    return {
        'categories': Category.objects.filter(forProducts=True),
        'menuItems': mi,
        'count': mi.count()+2,
        'offset': mi.count()+2
    }

@register.inclusion_tag('productCategories.djhtml')
def productCategories(name=None,*args,**kwargs):
    return {
        'asLink': 'asLink' in kwargs if True else False,
        'categories': Category.objects.filter(forProducts=True),
    }

@register.inclusion_tag('minicart.djhtml', takes_context = True)
def cartData(context,*args, **kwargs):
    request = context['request']
    if 'noButtons' in kwargs:
        noButtons = True
    else:
        noButtons = False
    if 'cartId' in request.session:
        items = CartProduct.objects.filter(cart__id = request.session['cartId'])
        return {
            'noButtons': noButtons,
            'items': items,
            'total': 'pln' + str(items.aggregate(
                total = Sum('price', field="price*quantity"))['total']),
            'count' : items.aggregate(Sum('quantity')).values()[0]
        }
    else:
        return {
            'items': [],
            'total': 0,
            'count' : 0,
        }


@register.inclusion_tag('cart.djhtml', takes_context = True)
def cartItems(context, *args, **kwargs):
    request = context['request']
    if 'orderId' in kwargs:
        cartId = Order.objects.get(id = kwargs['orderId']).cart.id
    elif 'cartId' in request.session:
        cartId = request.session['cartId']
    else:
        cartId = None
    if cartId:
        items = CartProduct.objects.filter(cart__id = cartId)
        return {
            'items': items,
            'total': 'pln'+str(items.aggregate(
                total = Sum('price', field="price*quantity"))['total']),
            'count' : items.aggregate(Sum('quantity')).values()[0]
        }
    else:
        return {
            'items': [],
            'total': 0,
            'count' : 0,
        }

@register.inclusion_tag('breadcrumbs.html', takes_context = True)
def breadcrumbs(context):
    res = [{'url':'/', 'name':_('home')}]
    els = context['request'].path.split('/')
    i = 1
    for e in els:
        if len(e) > 0:
            res.append( { 'url': '/'.join(els[0:i]), 'name':e } )
        i = i + 1
    return {
        'crumbs': res
    }

@register.inclusion_tag('quickContact.html')
def quickContact():
    return {
        'form': QuickContactForm
    }

@register.inclusion_tag('slider.html')
def slider(*args, **kwargs):
    slider = Slider.objects.get(name= kwargs['name'])
    return {
        'root': MEDIA_URL,
        'slider': slider,
        'slides': Slide.objects.filter(slider = slider)
    }