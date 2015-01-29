#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models, connection
from shop.settings import MEDIA_ROOT
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db.models import Sum, Count

class UserProfile(models.Model):
    pass

class Page(models.Model):
    title = models.CharField(max_length=100)
    body = RichTextField(max_length=20000)
    tags = models.ManyToManyField('Tag', related_name='pages', blank=True)
    categories = models.ManyToManyField('Category', related_name='pages', blank=True)
    attributes = models.ManyToManyField('Attribute', blank = True, null = True, related_name='pages')
    isMain = models.BooleanField(default=0)
    def __unicode__(self):
        return self.title

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

# Create your models here.
class Product(Page):
    name = models.CharField(max_length=100)
    shortName = models.CharField(max_length=100, default='', blank=True, null=True)
    description = RichTextField(max_length=2000, default='', blank=True, null=True)
    shortDescription = RichTextField(max_length=200, default='', blank=True, null=True)
    mainImage = models.FileField(upload_to='images/', default=None, blank=True)
    price = models.FloatField(default=0)
    def __unicode__(self):
        return self.name
    def getGroupedAttributes(self):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT ag.name, GROUP_CONCAT(a.name,', ') as atts 
            FROM amsoil_attribute a
            INNER JOIN amsoil_attributegroup ag ON ag.id=a.group_id
            INNER JOIN amsoil_page_attributes pa ON pa.attribute_id = a.id
            INNER JOIN amsoil_page p ON p.id = pa.page_id
                INNER JOIN amsoil_product pr ON pr.page_ptr_id = p.id
            WHERE p.id = %s 
            GROUP BY ag.id """ % self.id )
        return dictfetchall(cursor)
    def hasManyVariations(self):
        if self.getVariationsCount() > 1:
            return True
        else:
            return False
    def getVariationsDetails(self):
        res = []
        min = 100000
        for v in self.variations.all():
            if v.price < min:
                min = v.price
            res.append({ 'id':v.id, 'price':v.price, 'amount':v.amount })
        return {'min':min, 'vars':res}
    def getVariationsCount(self):
        return self.variations.count()
    def getVariations(self):
        options = {}
        for v in self.variations.all():
            for a in v.attributes.all():
                if not a.group.name in options:
                    options[a.group.name] = {}
                if not a.name in options[a.group.name]:
                    options[a.group.name][a.name] = []
                options[a.group.name][a.name].append( { 'id':v.id, 'price': v.price })
        return options
    def getMainImage(self):
        try:
            return self.mainImage.url
        except:
            return 'no image'

class ProductVariation(models.Model):
    product = models.ForeignKey(Product, related_name='variations')
    attributes = models.ManyToManyField('Attribute', related_name='products')
    name = models.CharField(max_length=100, blank=True, null=True)
    price = models.FloatField(default=0)
    image = models.ImageField(upload_to='images/',blank=True, null=True)
    amount = models.IntegerField(default=0)
    def getAttributesString(self):
        name = ''
        for a in self.attributes.all():
            name = name + " " + a.group.name + " " + a.name
        return name

class Category(models.Model):
    name = models.CharField(max_length=100)
    forProducts = models.BooleanField(default=False)
    image = models.FileField(upload_to=MEDIA_ROOT+'images/', default='', blank=True)
    def __unicode__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)

#class ProductImage(models.Model):
#    name = models.CharField(max_length=100)
#    file = models.FileField(upload_to=MEDIA_ROOT+'images/')
#    isMain = models.BooleanField(default=False)
#    product = models.ForeignKey(Product, related_name='images')jq

class Attachment(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to=MEDIA_ROOT+'files/')
    page = models.ForeignKey(Page, related_name='attachments')

class AttributeGroup(models.Model):
    name = models.CharField(max_length=100)
    forProductVariations = models.BooleanField(default=False)
    def __unicode__(self):
        return self.name

class Attribute(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100, blank = True, null = True)
    group = models.ForeignKey(AttributeGroup, related_name='attributes')
    def __unicode__(self):
        if self.group:
            return self.group.name + ' ' + self.name
        else:
            return self.name

def getProductAttributesByGroupName(name):
    return Attribute.objects.filter(group__name = name, pages__isnull = False).annotate(dcount=Count('id'))

class Menu(models.Model):
    name = models.CharField(max_length=100)
    def __unicode__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(blank=True, null=True, max_length=30)
    page = models.ForeignKey(Page, related_name='menuItems', blank=True, null=True)
    menu = models.ForeignKey(Menu)
    order = models.IntegerField(default=1)
    def __unicode__(self):
        try:
            return self.page.title
        except:
            return self.url
    def getUrl(self):
        try:
            return '/page/'+ str(self.page.id)
        except:
            return self.url

class CartProduct(models.Model):
    product = models.ForeignKey(Product,null = True, blank = True)
    cart = models.ForeignKey('Cart', related_name='cartProducts')
    quantity = models.IntegerField(default=1)
    price = models.FloatField(default=0)
    productVariation = models.ForeignKey(ProductVariation, default=None, null = True, blank = True)

class Cart(models.Model):
    type = models.CharField(choices=(('FI','finished'),('TE','temporary')),max_length=20)
    json = models.CharField(max_length=1000)
    #order = models.ForeignKey('Order', default = None,null = True)
    def getTotal(self):
        return self.cartProducts.aggregate(Sum('price')).values()[0]
    #quantity = models.IntegerField(default=1)
    #sessionId = models.CharField(max_length=20)

#class ProductOrder(models.Model):
#    product = models.ForeignKey(Product)
#    order = models.ForeignKey('Order')
#    quantity = models.IntegerField()
#    price = models.FloatField()

class Shipment(models.Model):
    class Meta:
        verbose_name = 'Adres'
        verbose_name_plural = 'Adresy'
    address = models.CharField(max_length=150)
    postalCode = models.CharField(max_length=6)
    phone = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    type = models.CharField(max_length=20,  choices=( ('BU','buyer'),('RE','receiver') ) )
    user = models.ForeignKey(User)
    order = models.ForeignKey('Order', related_name='shipment')
    def getTypeString(self):
        if self.type == 'RE':
            return 'Odbiorca'
        else:
            return 'Kupiec'
    def __unicode__(self):
        return self.getTypeString() + ':' + self.name + ' ' + self.surname

class Invoice(models.Model):
    NIP = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    user = models.ForeignKey(User, blank=True, null=True)
    order = models.ForeignKey('Order', blank=True, null=True)

class Method(models.Model):
    #class Meta:
    #    abstract = True
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank = True, null = True)
    def __unicode__(self):
        return self.name

class PaymentMethod(Method):
    instructions = models.CharField(max_length=500, blank = True, null = True)
    code = models.CharField(max_length='3')
    needsProcessing = models.BooleanField(default = False)
    price = models.FloatField(default=0, blank = True, null = True)

class ShippingMethod(Method):
    needsShipping = models.BooleanField(default = False)
    price = models.FloatField(default=0)
    paymentMethods = models.ManyToManyField(PaymentMethod, related_name='shippingMethods')
    pass

class Order(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    status = models.CharField(choices=(('PE','pending'),('CA','cancelled'),
                                       ('FI','finished')),max_length=20, default='PE')
    cart = models.ForeignKey(Cart)
    date = models.DateTimeField()
    shippingMethod = models.ForeignKey(ShippingMethod)
    paymentMethod = models.ForeignKey(PaymentMethod)
    notes = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField()

class MetaData(models.Model):
    class Meta:
        abstract = True
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=150)
    def get(self,key):
        try:
            v = self.objects.get(key = key).value
        except:
            v = None
        return v


class MethodOption(MetaData):
    method = models.ForeignKey(Method)

class PageMeta(MetaData):
    page = models.ForeignKey(Page)

class ShopMeta(MetaData):
    pass

class UserMeta(MetaData):
    user = models.ForeignKey(User)
    @staticmethod
    def getValue(user,key):
       try:
           return UserMeta.objects.get(user=user, key=key).value
       except:
           return False
    @staticmethod
    def setValue(user,key,value):
       try:
           um = UserMeta.objects.get(user=user,key=key)
           um.value = value
           um.save()
       except:
           um = UserMeta(key=key,value=value,user=user)
           um.save()


class Slider(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name
    def getSlidesCount(self):
        return self.slides.count()
    getSlidesCount.short_description = 'Liczba slajdów'

class Slide(models.Model):
    slider = models.ForeignKey(Slider, related_name='slides')
    title = models.CharField(max_length=200)
    text = models.CharField(max_length=500)
    button1Text = models.CharField(max_length=50, default='Read more')
    button1Url = models.CharField(max_length=50)
    button2Text = models.CharField(max_length=50, null=True, blank=True)
    button1Url = models.CharField(max_length=50, null=True, blank=True)
    product = models.ForeignKey(Product, blank=True, null=True)
    image = models.URLField(blank=True, null=True)
