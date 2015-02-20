#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import template
from amsoil.models import MenuItem, Category, CartProduct, Cart, Invoice, Shipment, Order, Slider, Slide, \
    Attribute, AttributeGroup, ProductVariation, UserMeta, Product
from amsoil.models import getProductAttributesByGroupName
from django.db.models import Sum, Count, Min, Max
from amsoil.forms import QuickContactForm
from django.utils.translation import ugettext as _
from shop.settings import MEDIA_URL
from amsoil.forms import ShippingForm


from django import template
from django.template import RequestContext
from django.template import Template

register = template.Library()

@register.inclusion_tag('tags/discount_info.html',takes_context=True)
def discount_info(context):
    request = context['request']
    if UserMeta.getValue(request.user,'discount'):
        return {
            'discount': {'ends': UserMeta.getValue(request.user,'discount_ends'),
                         'size': UserMeta.getValue(request.user,'discount') }
        }
    else:
        return {'discount': False}

@register.inclusion_tag('special_shop.html',takes_context=True)
def special_shop(context, *args, **kwargs):
    categories_names = kwargs['filters'].encode('utf8').split(',') if 'filters' in kwargs else []
    attributes_names = kwargs['attributes'].encode('utf8').split(',') if 'attributes' in kwargs else []
    attributes = Attribute.objects.filter(name__in = attributes_names)
    categories = Category.objects.filter(name__in = categories_names)
    attributes_ids = [a.id for a in attributes]
    categories_ids = [c.id for c in categories]

    return {
        'filters': kwargs['filters'].encode('utf8').split(',') if 'filters' in kwargs else [],
        'attributes': attributes_names,
        'categories': categories_names,
        'categories_ids': categories_ids,
        'attributes_ids': attributes_ids,
        'request': context['request']
    }


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
	return  "%.2f" % float(value) + ' zł'
	
def placeholder(value):
	value.field.widget.attrs["placeholder"] = value.help_text
	return value

register.filter(placeholder)


@register.inclusion_tag('sorter.html')
def sorter():
   return {
   }

@register.inclusion_tag('priceFilter.html', takes_context=True)
def priceFilter(context,limited=None,*args, **kwargs):
    if limited:
        products = get_products_query_set(context)
        pvs = ProductVariation.objects.filter(product__in = products)
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


@register.inclusion_tag('productCategories.djhtml', takes_context=True)
def productCategories(context, limited=None, name=None, *args, **kwargs):
    if limited:
        products = get_products_query_set(context)
        categories = Category.objects.filter(forProducts=True, pages__in = products).annotate(dcount=Count('pages__id'))
    else:
        categories = Category.objects.filter(forProducts=True).annotate(dcount=Count('pages__id'))
    return {
        'asLink': 'asLink' in kwargs if True else False,
        'categories': categories,
    }


@register.inclusion_tag('productFilter.html', takes_context=True)
def productFilter(context,limited=None, type=None, *args):
    if limited:
        products = get_products_query_set(context)
        #options = Attribute.objects.filter(group__name=type, pages__isnull=False, products__in = products).\
        #    annotate(dcount=Count('id'))
        options = Attribute.objects.filter(group__name=type, products__in = products).annotate(dcount=Count('products__id'))
    else:
        options = Attribute.objects.filter(group__name=type, pages__isnull=False).annotate(dcount=Count('products__id'))
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
        receiver = ShippingForm(instance=Shipment.objects.get(order=order,type='RE'))
    except:
        receiver = False
    try:
        buyer = ShippingForm(instance=Shipment.objects.get(order=order,type='BU'))
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


def get_products_query_set(context):
    pr = Product.objects.all()
    if 'attributes' in context.dicts[1]:
        pr = Product.objects.filter(attributes__name__in=context.dicts[1]['attributes'])
    if 'categories' in context.dicts[1]:
        pr = pr | Product.objects.filter(categories__name__in=context.dicts[1]['categories'])
    return pr