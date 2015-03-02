from django.contrib import admin
from amsoil.models import Menu, MenuItem, Product, Page, Category, ProductVariation, Attribute, AttributeGroup
from amsoil.models import ShippingMethod, PaymentMethod, Order, Cart, Invoice, Slider, Slide, Shipment, Post, Template
from amsoil.models import Attachment
from modeltranslation.admin import TranslationAdmin
from shop.settings import ADMIN_TEMPLATES_ROOT

# Register your models here.
admin.site.register(Menu)
admin.site.register(MenuItem)
admin.site.register(Category,TranslationAdmin)
admin.site.register(Attribute)
admin.site.register(AttributeGroup)
admin.site.register(ShippingMethod)
admin.site.register(PaymentMethod)

class TemplateAdmin(admin.ModelAdmin):
    model = Template
admin.site.register(Template, TemplateAdmin)


class PageAdmin(admin.ModelAdmin):
    model = Page
    def get_queryset(self, request):
        qs = super(PageAdmin, self).get_queryset(request)
        return qs.filter(product=None)

admin.site.register(Page, PageAdmin)

class SlideInline(admin.TabularInline):
    model = Slide

class SliderAdmin(admin.ModelAdmin):
    inlines = (SlideInline,)
    list_display = ('name','getSlidesCount')

class CartInline(admin.TabularInline):
    model = Cart
    #class Meta:
    #    model = Cart

class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 0

class ShipmentInline(admin.StackedInline):
    model = Shipment
    extra = 0
    exclude = ('user','type',)
    fields = ('getTypeString','name','surname','address','postalCode','phone')
    readonly_fields = ('getTypeString',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','number','status', 'date','email')
    inlines = (ShipmentInline, InvoiceInline,)
    readonly_fields = ('date',)
    change_form_template = ADMIN_TEMPLATES_ROOT + 'change_order.html'
    fields = ('status','number','date','paymentMethod','shippingMethod',
              'notes')

class VariationsInline(admin.TabularInline):
    model = ProductVariation
    fields = ('attributes','price','amount','total_sales','image',)
    readonly_fields = ('total_sales',)
    extra = 1

class AttachmentsInline(admin.TabularInline):
    model = Attachment
    fields = ('name','file','get_url',)
    readonly_fields = ('get_url',)
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = (VariationsInline, AttachmentsInline)
    list_display = ['name','mainImage']
    list_editable = ['name']
    search_fields = ['name']
    fields = ('name','shortName','description',('attributes','mainImage'),('categories','tags'),)
    #pass

class PostAdmin(admin.ModelAdmin):
    list_display = ['title','author']
    readonly_fields = ('created_at',)
    fields= ('title','url','body','created_at','author','categories','tags')
admin.site.register(Post, PostAdmin)

class ProductVariationAdmin(admin.ModelAdmin):
    model = ProductVariation
    search_fields = ['product']
    list_display = ['product','getAttributesString','price','amount','total_sales']
    list_editable = ['price','amount']

admin.site.register(ProductVariation, ProductVariationAdmin)

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Slider, SliderAdmin)
