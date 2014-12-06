from django.db import models
from shop.settings import MEDIA_ROOT
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db.models import Sum

class UserProfile(models.Model):
    pass

class Page(models.Model):
    title = models.CharField(max_length=100)
    body = RichTextField(max_length=20000)
    tags = models.ManyToManyField('Tag', related_name='pages', blank=True)
    categories = models.ManyToManyField('Category', related_name='pages', blank=True)
    isMain = models.BooleanField(default=0)
    def __unicode__(self):
        return self.title

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
    def getMainImage(self):
        try:
            return self.mainImage.url
        except:
            return 'no image'

class ProductVariation(models.Model):
    product = models.ForeignKey(Product, related_name='variations')
    attributes = models.ManyToManyField('Attribute', related_name='products')
    name = models.CharField(max_length=100)
    price = models.FloatField(default=0)
    image = models.ImageField(upload_to='images/')
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

class Attribute(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    group = models.ForeignKey(AttributeGroup, related_name='attributes')
    def __unicode__(self):
        if self.group:
            return self.group.name + ' ' + self.name
        else:
            return self.name

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
    address = models.CharField(max_length=150)
    postalCode = models.CharField(max_length=6)
    phone = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    type = models.CharField(max_length=20,  choices=( ('BU','buyer'),('RE','receiver') ) )
    user = models.ForeignKey(User)


class Invoice(models.Model):
    NIP = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    user = models.ForeignKey(User, blank=True, null=True)

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
    notes = models.CharField(max_length=200)
    receiver = models.ForeignKey(Shipment,related_name='receiverAddress', blank=True,null=True)
    buyer = models.ForeignKey(Shipment,related_name='buyerAddress', blank=True,null=True)
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