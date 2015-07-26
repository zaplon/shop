#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime, re, json
from django.db import models, connection
from shop.settings import MEDIA_ROOT, MEDIA_URL
from ckeditor.fields import RichTextField
from django.dispatch import receiver
from django.db.models.signals import pre_save, pre_delete, post_save
from django.db.models import Sum, Count, Min, F
import getpaid, hmac, requests
from django.core.urlresolvers import reverse
from authentication.models import User
from markitup.fields import MarkupField
from django.core import urlresolvers
from django.contrib.auth.models import Group
from hashlib import sha1
# from tinymce import models as tinymce_models

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
    attributes = models.ManyToManyField('Attribute', blank=True, null=True, related_name='pages',
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
        return s.replace('&nbsp;', ' ').replace('&#39;', "'")

    body = instance.body
    pattern = re.compile(r'\{%(.*?)\%}')
    instance.body = re.sub(pattern, do_replace, instance.body)
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
            GROUP BY ag.id """ % self.id)
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
            res.append({'id': int(v.id), 'price': float(v.price), 'amount': int(v.amount), 'image': image})
        return {'min': min, 'vars': res}

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
                    {'id': int(v.id), 'price': float(v.price)})
        return options

    def get_min_price(self):
        p = ProductVariation.objects.filter(product=self).aggregate(min_price=Min('price', field="price"))['min_price']
        return p

    def getMainImage(self):
        try:
            return self.mainImage.url
        except:
            return 'no image'


class ProductVariation(models.Model):
    @staticmethod
    def autocomplete_search_fields():
        return ("name__iexact", "product__name__icontains",)

    def __unicode__(self):
        pr = self.product.name
        for a in self.attributes.all():
            pr += ' ' + a.group.name + ' ' + a.name
        return pr

    class Meta:
        verbose_name = 'Wariant produktu'
        verbose_name_plural = 'Warianty produktów'

    product = models.ForeignKey(Product, related_name='variations')
    attributes = models.ManyToManyField('Attribute', related_name='products')
    name = models.CharField(max_length=100, blank=True, null=True)
    price = models.FloatField(default=0)
    purchase_price = models.FloatField(default=0, verbose_name="Cena zakupu")
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    amount = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)
    added_date = models.DateTimeField(auto_now=True)
    archoil_id = models.IntegerField(blank=True, null=True)

    def getAttributesString(self):
        name = ''
        for a in self.attributes.all():
            name = name + " " + a.group.name + " " + a.name
        return name


# @receiver(post_save, sender=ProductVariation)
# def post_product_save(instance, sender, **kwargs):
#     from WooCommerceClient import WooCommerceClient
#     wc_client = WooCommerceClient('ck_5e5692af317c09ca4581be6bc5596714', 'cs_3115cf0868e4ae29117257e13cec6248', 'http://archoil.pl/')
#
#     params = {
#          "variations":[
#               {
#                    "id":"81",
#                    "price":"10.00",
#                    "regular_price":"10.00",
#                    "attributes": [
#                         {
#                              "name":"pa_tamanho",
#                              "option":"m"
#                         },
#                         {
#                              "name":"pa_cor",
#                              "option":"verde"
#                         }
#                    ]
#               }
#          ]
#     }
#
#     wc_client.endpoint_call( '', params = {'quantity'} , method = 'GET' )

class Category(models.Model):
    class Meta:
        verbose_name = 'Kategoria'
        verbose_name_plural = 'Kategorie'

    name = models.CharField(max_length=100)
    forProducts = models.BooleanField(default=False)
    parent = models.ForeignKey('self', verbose_name='rodzic', blank=True, null=True, related_name='children')
    image = models.FileField(upload_to=MEDIA_ROOT + 'images/', default='', blank=True)
    order = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name


class Tag(models.Model):
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tagi'

    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


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
    file = models.FileField(upload_to=MEDIA_ROOT + 'files/', verbose_name='plik')
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
    value = models.CharField(max_length=100, blank=True, null=True)
    group = models.ForeignKey(AttributeGroup, related_name='attributes')

    def __unicode__(self):
        if self.group:
            return self.group.name + ' ' + self.name
        else:
            return self.name


def getProductAttributesByGroupName(name):
    return Attribute.objects.filter(group__name=name, pages__isnull=False).annotate(dcount=Count('id'))


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
    def get_actual_price(self):
        return self.productVariation.price

    get_actual_price.short_description = 'Aktualna cena'

    def get_mine_price(self, order_discount=False):
        pv = self.productVariation
        try:
            us = self.cart.order.user
        except:
            us = None

        #dla promocji nie ma juz znizek
        try:
            on_promotion = pv.product.categories.get(name__iexact='promocje')
            return pv.price
        except:
            pass
        if us is not None:
            #product_discounts = UserDiscount.objects.filter(product=pv) | \
            #                    UserDiscount.objects.filter(attribute__in=pv.product.attributes.all())
            discount = ( ( UserDiscount.objects.filter(user=us) |
                           UserDiscount.objects.filter(group__in=us.groups.all()) ) & \
                         (UserDiscount.objects.filter(product=pv) |
                          UserDiscount.objects.filter(attribute__in=pv.product.attributes.all()) )).order_by('value')
            if len(discount) > 0:
                discount = discount[0].value
            else:
                discount = 0
        else:
            discount = 0
        if not order_discount:
            order_discount = self.cart.getUserDiscount(us, True)
        if order_discount > discount:
            discount = order_discount
        return pv.price * (1 - float(discount) / 100)


    class Meta:
        verbose_name = 'Element koszyka'
        verbose_name_plural = 'Elementy koszyka'

    product = models.ForeignKey(Product, null=True, blank=True, verbose_name='Produkt')
    cart = models.ForeignKey('Cart', related_name='cartProducts')
    quantity = models.IntegerField(default=1, verbose_name='Ilość')
    price = models.FloatField(default=0, verbose_name='Cena')
    purchase_price = models.FloatField(default=0, verbose_name="Cena zakupu")
    productVariation = models.ForeignKey(ProductVariation, default=None, null=True, blank=True,
                                         related_name='cartProduct', verbose_name='Wariant produktu')


class UserDiscount(models.Model):
    def __unicode__(self):
        if self.user:
            return str(self.user) + ' ' + str(self.value)
        if self.group:
            return str(self.group.name) + ' ' + str(self.value)
        else:
            return str(self.value) + '%'

    class Meta:
        verbose_name = 'Zniżka'
        verbose_name_plural = 'Zniżki'

    user = models.ForeignKey(User, related_name='discounts', verbose_name='Użytkownik', blank=True, null=True)
    group = models.ForeignKey(Group, related_name='discounts', verbose_name='Grupa użytkowników', blank=True, null=True)
    attribute = models.ForeignKey(Attribute, blank=True, null=True, verbose_name='Atrybut')
    product = models.ForeignKey(ProductVariation, blank=True, null=True, verbose_name='Produkt')
    value = models.FloatField(default=0, verbose_name='Wysokość zniżki w %')


class Cart(models.Model):
    def __unicode__(self):
        return str(self.id)

    def updatePrices(self):
        td = 0
        t = 0
        for cp in self.cartProducts.all():
            cp.price = cp.get_mine_price()
            cp.save()
        try:
            self.order
        except:
            return True

    class Meta:
        verbose_name = 'Koszyk'
        verbose_name_plural = 'Koszyki'

    type = models.CharField(choices=(('FI', 'finished'), ('TE', 'temporary')), max_length=20, default='FI')
    json = models.CharField(max_length=1500, default='{}')
    #user = models.ForeignKey(User, blank=True, null=True)
    #order = models.ForeignKey('Order', default = None,null = True)
    def getTotal(self):
        total = CartProduct.objects.filter(cart=self).aggregate(total=Sum('price', field="price*quantity"))['total']
        if not total:
            return 0
        else:
            return total

    getTotal.short_description = 'Produkty w sumie'

    def getDiscount(self, user=None, as_percent=False):
        cps = CartProduct.objects.filter(cart=self)
        d = 0
        for cp in cps:
            d += (cp.productVariation.price - cp.price) * cp.quantity
        return d
        #return CartProduct.objects.filter(cart=self).aggregate(total=Sum('price', field="price*quantity"))['total']

    def getUserDiscount(self, user, as_percent=False):
        discount = 0
        database_discount = 0

        on_promotion = self.cartProducts.filter(productVariation__product__categories__name__iexact='Promocje').values(
            'price', 'quantity')

        promotion_price = sum(r['price'] * r['quantity'] for r in on_promotion)

        total = self.getTotal() - int(promotion_price)
        if total >= 1000:
            discount = 20
        elif total >= 500:
            discount = 15
        elif total >= 300:
            discount = 10
        if user and user.is_authenticated():
            if UserMeta.getValue(user, 'discount'):
                database_discount = UserMeta.getValue(user, 'discount')
        if int(database_discount) > discount:
            try:
                if not as_percent:
                    discount = total * float(UserMeta.getValue(user, 'discount')) / 100
                else:
                    discount = float(UserMeta.getValue(user, 'discount'))
            except:
                pass
        else:
            if total is not None and not as_percent:
                discount = total * discount / 100
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
    city = models.CharField(max_length=150, verbose_name='Miejscowość')
    type = models.CharField(max_length=20, choices=( ('BU', 'buyer'), ('RE', 'receiver') ))
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

    def __unicode__(self):
        return self.name
    NIP = models.CharField(max_length=20)
    name = models.CharField(max_length=100, verbose_name='Nazwa')
    address = models.CharField(max_length=150, verbose_name='Adres')
    postalCode = models.CharField(max_length=6, verbose_name='Kod')
    city = models.CharField(max_length=150, verbose_name='Miejscowość')
    user = models.OneToOneField(User, blank=True, null=True)
    order = models.OneToOneField('Order', blank=True, null=True, related_name='invoice')


class Method(models.Model):
    #class Meta:
    #    abstract = True
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True, null=True)
    is_enabled = models.BooleanField(default=True, verbose_name='Włączona')

    def __unicode__(self):
        return self.name


class PaymentMethod(Method):
    class Meta:
        verbose_name = 'Metoda zapłaty'
        verbose_name_plural = 'Metody zapłaty'

    instructions = models.CharField(max_length=500, blank=True, null=True)
    code = models.CharField(max_length='3')
    needsProcessing = models.BooleanField(default=False)
    price = models.FloatField(default=0, blank=True, null=True)


class ShippingMethod(Method):
    class Meta:
        verbose_name = 'Metoda wysyłki'
        verbose_name_plural = 'Metody wysyłki'

    needsShipping = models.BooleanField(default=False)
    price = models.FloatField(default=0)
    instructions = models.CharField(max_length=500, blank=True, null=True)
    paymentMethods = models.ManyToManyField(PaymentMethod, related_name='shippingMethods')
    pass


class Order(models.Model):
    class Meta:
        verbose_name = 'Zamówienie'
        verbose_name_plural = 'Zamówienia'

    user = models.ForeignKey(User, null=True, blank=True, verbose_name='Użytkownik')
    status = models.CharField(choices=(('PE', 'PENDING'), ('CA', 'CANCELLED'),
                                       ('FI', 'FINISHED'), ('WC', 'WAITING FOR CASH')), max_length=20, default='PE')
    cart = models.OneToOneField(Cart, related_name='order')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Data')
    shippingMethod = models.ForeignKey(ShippingMethod, verbose_name='Metoda wysyłki')
    paymentMethod = models.ForeignKey(PaymentMethod, verbose_name='Metoda zapłaty')
    notes = models.CharField(max_length=200, blank=True, null=True, verbose_name='Uwagi')
    email = models.EmailField(verbose_name='Email')
    number = models.CharField(max_length=20, default='', verbose_name='Numer zamówienia', blank=True, null=True)
    phone = models.CharField(max_length=15, default=0, verbose_name='Telefon')
    total = models.FloatField(default=0, verbose_name='W sumie')
    token = models.CharField(max_length=30, blank=True, null=True)
    paypalData = models.CharField(max_length=300, blank=True, null=True)
    discount = models.FloatField(default=0, verbose_name='Zniżka')
    mail_sended = models.BooleanField(default=False, verbose_name='Mail przesłany')
    archoil_id = models.IntegerField(default=0)
    income = models.FloatField(default=0, verbose_name='Zysk')
    margin = models.FloatField(default=0, verbose_name='Marża')
    in_ifirma = models.BooleanField(default=False, verbose_name='Zaksięgowane')
    free_shipping = models.BooleanField(default=False, verbose_name='Darmowa wysyłka')
    deadline = models.DateTimeField(verbose_name='Termin płatności')

    def get_income(self):
        return CartProduct.objects.aggregate(total=Sum('price', field='price-purchase_price'))['total']
    def get_margin(self):
        return CartProduct.objects.aggregate(total=Sum('price', field='(price-purchase_price)/purchase_price'))['total']
    def ifirma(self):
        instance = self
            #api ifirma
        # requestContent = '{"Zaplacono":78,"LiczOd":"BRT","NumerKontaBankowego":null,' \
        #                  '"DataWystawienia":"2010-03-25","MiejsceWystawienia":"Miasto",' \
        #                  '"DataSprzedazy":"2010-03-25","FormatDatySprzedazy":"DZN",' \
        #                  '"TerminPlatnosci":null,"SposobZaplaty":"PRZ",' \
        #                  '"NazwaSeriiNumeracji":"default","NazwaSzablonu":"logo",' \
        #                  '"RodzajPodpisuOdbiorcy":"OUP","PodpisOdbiorcy":"Odbiorca",' \
        #                  '"PodpisWystawcy":"Wystawca","Uwagi":"uwagi","WidocznyNumerGios":true,' \
        #                  '"Numer":null,"Pozycje":[{"StawkaVat":0.23,"Ilosc":1,' \
        #                  '"CenaJednostkowa":78.00,"NazwaPelna":"cos","Jednostka":"sztuk","PKWiU":"",' \
        #                  '"TypStawkiVat":"PRC"}],"Kontrahent":' \
        #                  '{"Nazwa":"Imie Nazwisko","Identyfikator":null,"PrefiksUE":null,' \
        #                  '"NIP":null,"Ulica":"Ulica","KodPocztowy":"11-111","Kraj":"Polska",' \
        #                  '"Miejscowosc":"Miejscowość","Email":"em@il.pl","Telefon":"111111111",' \
        #                  '"OsobaFizyczna":true}}'
        nr = '14116022020000000213128273'
        dt = instance.date.strftime('%Y-%m-%d')
        if instance.paymentMethod.code == 'prz':
            sz = 'PRZ'
        elif instance.paymentMethod.code == 'tr':
            sz = ' KAR'
        else:
            sz = 'GTK'
        poz = []

        try:
            instance.invoice
            inv = True
        except:
            inv = False

        for cp in instance.cart.cartProducts.all():
            if inv:
                poz.append({'StawkaVat':0.23, 'Ilosc': cp.quantity, 'CenaJednostkowa': cp.price,
                            'NazwaPelna': cp.productVariation.product.name + ' ' + cp.productVariation.getAttributesString(),
                            'Jednostka': 'sztuk', 'PKWiU':'', 'TypStawkiVat':'PRC'})
            else:
                poz.append({'Ilosc': cp.quantity, 'CenaJednostkowa': cp.price,
                            'NazwaPelna': cp.productVariation.product.name + ' ' + cp.productVariation.getAttributesString(),
                            'Jednostka': 'sztuk'})

        #koszt przesylki
        if instance.shippingMethod.price > 0:
            if inv:
                poz.append({'StawkaVat':0.23, 'Ilosc': 1, 'CenaJednostkowa': instance.shippingMethod.price,
                            'NazwaPelna': instance.shippingMethod.name, 'Jednostka': 'sztuk', 'PKWiU':'', 'TypStawkiVat':'PRC'})
            else:
                poz.append({'Ilosc': 1, 'CenaJednostkowa': instance.shippingMethod.price, 'NazwaPelna': instance.shippingMethod.name,
                            'Jednostka': 'sztuk'})

        if inv:
            tr = instance.deadline.strftime('%Y-%m-%d')
            inv = instance.invoice
            key = '904567BFF6B88C50'
            key_name = 'faktura'
            url = 'https://www.ifirma.pl/iapi/fakturakraj.json'
            kon = {'Nazwa': inv.name, 'NIP': inv.NIP.replace('-',''), 'Email': instance.email, 'Ulica': inv.address, 'Miejscowosc': inv.city,
                   'KodPocztowy': inv.postalCode, 'JestDostawca': False }
            if instance.user:
                kon['Identyfikator'] = instance.user.id
            req = {'Zaplacono': instance.total, 'LiczOd':'BRT', 'NumerKontaBankowego': nr, 'DataWystawienia': dt, 'MiejsceWystawienia':'Warszawa',
                   'DataSprzedazy': dt, 'FormatDatySprzedazy':'DZN', 'TerminPlatnosci': tr, 'SposobZaplaty':sz, "RodzajPodpisuOdbiorcy": "OUP",
                   'WidocznyNumerGios': True, 'Numer': None, 'Pozycje': poz, 'Kontrahent': kon}
            if instance.user:
                req['IdentyfikatorKontrahenta'] = instance.user.id
            req = json.dumps(req)
            hash = hmac.new(key.decode('hex'),url+'info@najlepszysyntetyk.pl'+key_name+req, sha1)
            hash_string = hash.hexdigest()
            headers = {'Accept': 'application/json',
                   'Content-type': 'application/json; charset=UTF-8',
                   'Authentication': 'IAPIS user=info@najlepszysyntetyk.pl, hmac-sha1=' + hash_string }
            res = requests.post(url, headers=headers, data=req)

        else:
            return False
            key = 'D7377223A92F12D2'
            key_name = 'rachunek'
            url = 'https://www.ifirma.pl/iapi/rachunekkraj.json'
            rec = Shipment.objects.get(order=instance, type='BU')
            kon = {'Nazwa': rec.name + ' ' + rec.surname, 'Ulica': rec.address, 'KodPocztowy': rec.postalCode, 'Miejscowosc': rec.city,
                   'JestDostawca': False, 'OsobaFizyczna': True}
            if instance.user:
                kon['Identyfikator'] = instance.user.id
            # '{"Zaplacono": 78,"NumerKontaBankowego": null,"DataWystawienia": "2010-03-25","MiejsceWystawienia": "Miasto",' \
            # '"DataSprzedazy": "2010-03-25","FormatDatySprzedazy": "DZN","TerminPlatnosci": null,"SposobZaplaty": "PRZ",' \
            # '"NazwaSeriiNumeracji": "default","NazwaSzablonu": "logo","WpisDoKpir": "TOW","PodpisOdbiorcy": "Odbiorca",' \
            # '"PodpisWystawcy": "Wystawca","Uwagi": "uwagi","Numer": null,"Pozycje":[{"Ilosc": 1,"CenaJednostkowa": 78,' \
            # '"NazwaPelna": "cos","Jednostka": "sztuk"}],"Kontrahent":{"Nazwa": "Imie Nazwisko","Identyfikator": null,' \
            # '"PrefiksUE": null,"NIP": null,"Ulica": "Ulica","KodPocztowy": "11-111","Kraj": "Polska","Miejscowosc": "Miejscowość",' \
            # '"Email": "em@il.pl","Telefon": "111111111","OsobaFizyczna": true}}';

            req = {'Zaplacono': instance.total, 'NumerKontaBankowego': nr, 'DataWystawienia': dt, 'MiejsceWystawienia': 'Warszawa',
                   'DataSprzedazy': dt, 'FormatDatySprzedazy': 'DZN', 'TerminPlatnosci': None, 'SposobZaplaty': sz, 'Pozycje': poz,
                   'Kontrahent': kon, 'WpisDoKpir':'TOW', 'Numer': None}
            if instance.user:
                req['IdentyfikatorKontrahenta'] = instance.user.id

            req = json.dumps(req)
            hash = hmac.new(key.decode('hex'),url+'info@najlepszysyntetyk.pl'+key_name+req, sha1)
            hash_string = hash.hexdigest()
            headers = {'Accept': 'application/json',
                   'Content-type': 'application/json; charset=UTF-8',
                   'Authentication': 'IAPIS user=info@najlepszysyntetyk.pl, hmac-sha1=' + hash_string }
            res = requests.post(url, headers=headers, data=req)

        #res = json.loads(res)
        try:
            code = json.loads(res.text)['response']['Kod']
            if code == 0:
                return True
            else:
                return False
        except:
            return False
    def get_cart_url(self):
        if self.cart:
            link = urlresolvers.reverse("admin:%s_%s_change" %
                                        (self._meta.app_label, 'cart'), args=(self.cart.pk,))
            return '<a target="_blank" href="%s">Edytuj</a>' % link
        else:
            return ''

    get_cart_url.short_description = 'Koszyk'

    def get_status(self):
        return self.status

    def resend_mail(self):
        return '<div id="resend-mail" class="admin-button"  data-id=' + str(self.id) + '>Wyślij mail</div>'

    resend_mail.short_description = 'Wyślij mail ponownie'

    def get_absolute_url(self):
        return reverse('checkout-processed', kwargs={'pk': self.pk})

    def __unicode__(self):
        return 'Zamowienie nr ' + self.number


getpaid.register_to_payment(Order, unique=False, related_name='payments')


@receiver(pre_save, sender=CartProduct)
def addBoughtPrice(instance, sender, **kwargs):
    instance.purchase_price = instance.productVariation.purchase_price

@receiver(pre_save, sender=Order)
def createOrderNr(instance, sender, **kwargs):
    try:
        instance.cart
        instance.total = instance.cart.getTotal() + instance.paymentMethod.price
        if not instance.free_shipping:
            instance.total += instance.shippingMethod.price
        instance.discount = instance.cart.getDiscount()
        instance.income = instance.get_income()
        instance.margin = instance.get_margin()
    except:
        c = Cart()
        c.save()
        instance.cart = c

    #zmniejszamy stany magazynowe
    for cp in instance.cart.cartProducts.all():
        pv = cp.productVariation
        pv.amount -= cp.quantity
        pv.total_sales += cp.quantity
        pv.save()

    #dodajemy adresy i faktury jeśli trzeba
    if len(instance.shipment.all()) == 0:
        shs = Shipment.objects.filter(user=instance.user)
        for s in shs:
            s.id = None
            s.order = instance
            s.save()
    try:
        instance.invoice
    except:
        try:
            inv = Invoice.objects.get(user=instance.user)
            inv.NIP = inv.NIP.replace('-','')
            inv.id = None
            inv.order = instance
            inv.user = None
            inv.save()
        except:
            pass

    if instance.status == 'FI' and not instance.in_ifirma:
        if instance.ifirma():
            instance.in_ifirma = True


    instance.number = str(datetime.datetime.now().strftime('%s'))
    if not instance.deadline:
        instance.deadline = ( datetime.datetime.now() + datetime.timedelta(days=7) )


@receiver(pre_save, sender=Cart)
def preCartSave(instance, sender, **kwargs):
    #if cp.cart.order.status is not 'FINISHED':
    instance.updatePrices()


@receiver(pre_delete, sender=Order)
def correctQuantities(instance, sender, **kwargs):
    for cp in instance.cart.cartProducts.all():
        pv = cp.productVariation
        pv.amount += cp.quantity
        pv.total_sales -= cp.quantity
        pv.save()


class MetaData(models.Model):
    class Meta:
        abstract = True

    key = models.CharField(max_length=50)
    value = models.CharField(max_length=150)

    def get(self, key):
        try:
            v = self.objects.get(key=key).value
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
    def getValue(user, key):
        try:
            return UserMeta.objects.get(user=user, key=key).value
        except:
            return False

    @staticmethod
    def setValue(user, key, value):
        try:
            um = UserMeta.objects.get(user=user, key=key)
            um.value = value
            um.save()
        except:
            um = UserMeta(key=key, value=value, user=user)
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
    class Meta:
        verbose_name = 'Odbiorca newslettera'
        verbose_name_plural = 'Odbiorcy newsletterów'

    email = models.EmailField(unique=True)
    token = models.CharField(max_length=30)

    def __unicode__(self):
        return self.email

    @staticmethod
    def get_token():
        return datetime.datetime.now().strftime('%s')


@receiver(pre_save, sender=NewsletterReceiver)
def pre_receiver_save(instance, sender, **kwargs):
    if not instance.email:
        instance.email = instance.token + '@wp.pl'
    return True


#@receiver(pre_save, sender=NewsletterReceiver)
#def ensure_receiver_not_exists(instance, sender, **kwargs):
#    if len(NewsletterReceiver.objects.filter(email=instance.email)) > 0:
#        return False
#    return True

import payments