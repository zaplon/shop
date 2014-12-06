from django.contrib import admin
from amsoil.models import Menu, MenuItem, Product, Page, Category, ProductVariation, Attribute, AttributeGroup
from amsoil.models import ShippingMethod, PaymentMethod, Order, Cart
from modeltranslation.admin import TranslationAdmin
from shop.settings import ADMIN_TEMPLATES_ROOT

# Register your models here.
admin.site.register(Menu)
admin.site.register(MenuItem)
admin.site.register(Page)
admin.site.register(Category,TranslationAdmin)
admin.site.register(Attribute)
admin.site.register(ProductVariation)
admin.site.register(ShippingMethod)
admin.site.register(PaymentMethod)

class CartInline(admin.TabularInline):
    model = Cart
    #class Meta:
    #    model = Cart

class OrderAdmin(admin.ModelAdmin):
    list_display = ('status', 'date')
    #inlines = (CartInline,)
    change_form_template = ADMIN_TEMPLATES_ROOT + 'change_order.html'
    fields = ('status','date','paymentMethod','shippingMethod',
              'notes','receiver','buyer')


class VariationsInline(admin.TabularInline):
    model = ProductVariation

class ProductAdmin(admin.ModelAdmin):
    inlines = (VariationsInline,)
    fields = ('name','shortName','description',('price','mainImage'),('categories','tags'),)
    #pass


admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)