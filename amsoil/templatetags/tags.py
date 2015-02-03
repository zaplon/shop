#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import template
from amsoil.models import MenuItem, Category, CartProduct, Cart, Invoice, Shipment, Order, Slider, Slide, \
    Attribute, AttributeGroup, ProductVariation
from amsoil.models import getProductAttributesByGroupName    
from django.db.models import Sum, Count
from amsoil.forms import QuickContactForm
from django.utils.translation import ugettext as _
from shop.settings import MEDIA_URL


register = template.Library()

@register.inclusion_tag('productsTabs.html')
def productsTabs():
    newest = ProductVariation.objects.all().order_by('added_date')[0:5]
    best = ProductVariation.objects.all().order_by('total_sale')[0:5]
    promo = ProductVariation.objects.filter(product__categories__name = 'promotion')[0:5]
    return {
        'cats': {
            'newest': newest.count() == 0 if False else { 'name': 'Nowości', 'id': 'newest', 'products':newest, 
                                                          'width': newest.count() >0 if int(12/newest.count()) else 0 },
            'best': best.count() == 0 if False else { 'name': 'Bestsellery', 'id': 'best', 'products':best,
                                                      'width':best.count() >0 if int(12/newest.count()) else 0 },
            'promo': promo.count() == 0 if False else { 'name': 'Promocje', 'id': 'promo', 'products':promo, 
                                                        'width':promo.count() >0 if int(12/newest.count()) else 0 }
        }
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
        'count': mi.count()+2,
        'offset': mi.count()+2
    }

@register.inclusion_tag('productCategories.djhtml')
def productCategories(name=None,*args,**kwargs):
    return {
        'asLink': 'asLink' in kwargs if True else False,
        'categories': Category.objects.filter(forProducts=True),
    }

@register.inclusion_tag('productFilter.html')
def productFilter(type = None,*args):
    options = Attribute.objects.filter(group__name = type, pages__isnull = False).annotate(dcount=Count('id'))
    return {
        'options': options,
        'type': type
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
            'noButtons': True if 'noButtons' in kwargs else False,
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
            if e != 'product' and e != 'category':
                res.append( { 'url': '/'.join(els[0:i]), 'name':e} )
        i = i + 1
    res[-1]['last'] = True
    return {
        'crumbs': res
    }

@register.inclusion_tag('quickContact.html', takes_context = True)
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
    slider = Slider.objects.get(name= kwargs['name'])
    return {
        'root': MEDIA_URL,
        'slider': slider,
        'slides': Slide.objects.filter(slider = slider)
    }
