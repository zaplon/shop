#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime, re, json
from django.db import models, connection
from shop.settings import MEDIA_ROOT, MEDIA_URL
from ckeditor.fields import RichTextField
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db.models import Sum, Count
import getpaid
from django.core.urlresolvers import reverse
from authentication.models import User
from markitup.fields import MarkupField
#from tinymce import models as tinymce_models

class UserProfile(models.Model):
    pass

class Template(models.Model):
    class Meta:
        verbose_name = 'Szablon'
        verbose_name_plural = 'Szablony'
    name = models.CharField(max_length=100)
    body = MarkupField()
    def __unicode__(self):
        return self.name

class Page(models.Model):
    class Meta:
        verbose_name = 'Strona'
        verbose_name_plural = 'Strony'
    title = models.CharField(max_length=100)
    body = RichTextField(max_length=20000)
    url = models.CharField(default='', max_length=100)
    tags = models.ManyToManyField('Tag', related_name='pages', blank=True, verbose_name='Tagi')
    categories = models.ManyToManyField('Category', related_name='pages', blank=True,
                                        verbose_name='Kategorie')
    attributes = models.ManyToManyField('Attribute', blank = True, null = True, related_name='pages',
                                        verbose_name='Atrybuty')
    isMain = models.BooleanField(default=0)
    full_width = models.BooleanField(default=0, verbose_name='Szerokość całej strony')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Utworzono')
    is_published = models.BooleanField(default=True, verbose_name='Opublikowane')
    def __unicode__(self):
        return self.title

class Post(Page):
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posty'
    author = models.ForeignKey(User, blank=True, null=True)

@receiver(pre_save, sender=Post)
def format_post_url(instance, sender, **kwargs):
    if instance.url == '':
        instance.url = instance.title


@receiver(pre_save, sender=Page)
def prepare_page_data(instance, sender, **kwargs):
     def do_replace(m):
        s = m.group(0)
        return s.replace('&nbsp;',' ').replace('&#39;',"'")
     body = instance.body
     pattern = re.compile(r'\{%(.*?)\%}')
     instance.body = re.sub(pattern,do_replace,instance.body)
     return True




def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

# Create your models here.
class Product(Page):
    class Meta:
        verbose_name = 'Produkt'
        verbose_name_plural = 'Produkty'
    name = models.CharField(max_length=100)
    shortName = models.CharField(max_length=100, default='', blank=True, null=True,
                                 verbose_name='Krótka nazwa')
    description = RichTextField(default='', blank=True, null=True, verbose_name='Opis')
    shortDescription = RichTextField(max_length=200, default='', blank=True, null=True,
                                     verbose_name='Krótki opis')
    mainImage = models.FileField(upload_to='images/', default=None, blank=True,
                                 verbose_name='Główne zdjęcie')
    price = models.FloatField(default=0, verbose_name='Cena')
    def __unicode__(self):
        return self.name
    def getGroupedVariations(self):
        cursor = connection.cursor()
        cursor.execute("""
        SELECT ag.name, GROUP_CONCAT(CONCAT('[', a.name, ', ', pv.id, ']') ORDER BY ag.name SEPARATOR ', ') as atts
            FROM amsoil_attribute a
            INNER JOIN amsoil_attributegroup ag ON ag.id=a.group_id
            INNER JOIN amsoil_productvariation_attributes pa ON pa.attribute_id = a.id
                INNER JOIN amsoil_productvariation pv ON pv.id = pa.productvariation_id
                INNER JOIN amsoil_product p ON pv.product_id = p.page_ptr_id
            WHERE p.page_ptr_id = %s
            GROUP BY ag.id
        """ % self.id)
        return dictfetchall(cursor)
    def getGroupedAttributes(self):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT ag.name, GROUP_CONCAT(a.name ORDER BY ag.name SEPARATOR ', ') as atts
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
                if v.image:
                    image = image.url
                else:
                    image = False
            res.append({ 'id':int(v.id), 'price':float(v.price), 'amount':int(v.amount), 'image': image })
        return {'min':min, 'vars':res}
    def getVariationsCount(self):
        return self.variations.count()
    def getVariations(self):
        options = {}
        for v in self.variations.all().order_by('price'):
            for a in v.attributes.all():
                if not a.group.name.encode('utf-8') in options:
                    options[a.group.name.encode('utf-8')] = {}
                if not a.name.encode('utf-8') in options[a.group.name.encode('utf-8')]:
                    options[a.group.name.encode('utf-8')][a.name.encode('utf-8')] = []
                options[a.group.name.encode('utf-8')][a.name.encode('utf-8')].append(
                    { 'id':int(v.id), 'price': float(v.price) })
        return options
    def getMainImage(self):
        try:
            return self.mainImage.url
        except:
            return 'no image'

class ProductVariation(models.Model):
    class Meta:
        verbose_name = 'Wariant produktu'
        verbose_name_plural = 'Warianty produktów'
    product = models.ForeignKey(Product, related_name='variations')
    attributes = models.ManyToManyField('Attribute', related_name='products')
    name = models.CharField(max_length=100, blank=True, null=True)
    price = models.FloatField(default=0)
    image = models.ImageField(upload_to='images/',blank=True, null=True)
    amount = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)
    added_date = models.DateTimeField(auto_now=True)
    def getAttributesString(self):
        name = ''
        for a in self.attributes.all():
            name = name + " " + a.group.name + " " + a.name
        return name

class Category(models.Model):
    class Meta:
        verbose_name = 'Kategoria'
        verbose_name_plural = 'Kategorie'
    name = models.CharField(max_length=100)
    forProducts = models.BooleanField(default=False)
    parent = models.ForeignKey('self', verbose_name='rodzic', blank=True, null=True, related_name='children')
    image = models.FileField(upload_to=MEDIA_ROOT+'images/', default='', blank=True)
    order = models.IntegerField(default=0)
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
    class Meta:
        verbose_name = 'załącznik'
        verbose_name_plural = 'załączniki'
    name = models.CharField(max_length=100, verbose_name='nazwa')
    file = models.FileField(upload_to=MEDIA_ROOT+'files/', verbose_name='plik')
    page = models.ForeignKey(Page, related_name='attachments')
    def get_url(self):
        return MEDIA_URL + 'files/' + self.file.name.split('/')[-1]
    get_url.short_description = 'link'

class AttributeGroup(models.Model):
    class Meta:
        verbose_name = 'Grupa atrybutów'
        verbose_name_plural = 'Grupy atrybutów'
    name = models.CharField(max_length=100)
    forProductVariations = models.BooleanField(default=False)
    def __unicode__(self):
        return self.name

class Attribute(models.Model):
    class Meta:
        verbose_name = 'Atrybut'
        verbose_name_plural = 'Atrybuty'
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
            return str(self.page.title)
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
        total = CartProduct.objects.filter(cart=self).aggregate(total=Sum('price', field="price*quantity"))['total']
        if not total:
            return 0
        else:
            return total
    def getDiscount(self,user):
        discount = 0
        database_discount = 0

        on_promotion = self.cartProducts.all().filter(product__categories__name='Promocje').values('price', 'quantity')

        promotion_price = sum(r['price']*r['quantity'] for r in on_promotion)

        total = self.getTotal() - int(promotion_price)
        if total >= 1000:
            discount = 20
        elif total >= 500:
            discount = 15
        elif total >= 300:
            discount = 10
        if user.is_authenticated():
            if UserMeta.getValue(user,'discount'):
                database_discount = UserMeta.getValue(user,'discount')
        if int(database_discount) > discount:
            try:
                discount = total * float(UserMeta.getValue(user,'discount'))/100
            except:
                pass
        else:
            if total is not None:
                discount = total * discount/100
        return discount
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
    address = models.CharField(max_length=150, verbose_name='Adres')
    postalCode = models.CharField(max_length=6, verbose_name='Kod pocztowy')
    phone = models.CharField(max_length=15, verbose_name='Telefon')
    name = models.CharField(max_length=100, verbose_name='Imię')
    surname = models.CharField(max_length=100, verbose_name='Nazwisko')
    type = models.CharField(max_length=20,  choices=( ('BU','buyer'),('RE','receiver') ) )
    user = models.ForeignKey(User, blank=True, null=True)
    order = models.ForeignKey('Order', related_name='shipment', blank=True, null=True)
    def getTypeString(self):
        if self.type == 'RE':
            return 'Odbiorca'
        else:
            return 'Kupiec'
    def __unicode__(self):
        return self.getTypeString() + ':' + self.name + ' ' + self.surname

class Invoice(models.Model):
    class Meta:
        verbose_name = 'Faktura'
        verbose_name_plural = 'Faktury'
    NIP = models.CharField(max_length=20)
    name = models.CharField(max_length=100, verbose_name='Nazwa')
    address = models.CharField(max_length=150, verbose_name='Adres')
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
    class Meta:
        verbose_name = 'Metoda zapłaty'
        verbose_name_plural = 'Metody zapłaty'
    instructions = models.CharField(max_length=500, blank = True, null = True)
    code = models.CharField(max_length='3')
    needsProcessing = models.BooleanField(default = False)
    price = models.FloatField(default=0, blank = True, null = True)

class ShippingMethod(Method):
    class Meta:
        verbose_name = 'Metoda wysyłki'
        verbose_name_plural = 'Metody wysyłki'
    needsShipping = models.BooleanField(default = False)
    price = models.FloatField(default=0)
    paymentMethods = models.ManyToManyField(PaymentMethod, related_name='shippingMethods')
    pass

class Order(models.Model):
    class Meta:
        verbose_name = 'Zamówienie'
        verbose_name_plural = 'Zamówienia'
    user = models.ForeignKey(User, null=True, blank=True)
    status = models.CharField(choices=(('PE','Oczekujące'),('CA','Anulowane'),
                                       ('FI','Zakończone')),max_length=20, default='PE')
    cart = models.ForeignKey(Cart)
    date = models.DateTimeField(auto_now=True)
    shippingMethod = models.ForeignKey(ShippingMethod)
    paymentMethod = models.ForeignKey(PaymentMethod)
    notes = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField()
    number = models.CharField(max_length=20, default='')
    phone = models.CharField(max_length=15, default=0)
    total = models.FloatField(default=0)
    token = models.CharField(max_length=30, blank=True, null=True)
    paypalData = models.CharField(max_length=300, blank=True, null=True)
    def get_absolute_url(self):
        return reverse('checkout-processed', kwargs={'pk': self.pk})

getpaid.register_to_payment(Order, unique=False, related_name='payments')

@receiver(pre_save, sender=Order)
def createOrderNr(instance, sender, **kwargs):
    instance.number = str(datetime.datetime.now().strftime('%s'))


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
    image = models.ImageField(verbose_name='obrazek')
    order = models.IntegerField(default=0, verbose_name='Kolejność')

class NewsletterReceiver(models.Model):
    email = models.EmailField(unique=True)

#@receiver(pre_save, sender=NewsletterReceiver)
#def ensure_receiver_not_exists(instance, sender, **kwargs):
#    if len(NewsletterReceiver.objects.filter(email=instance.email)) > 0:
#        return False
#    return True

