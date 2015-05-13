from django.contrib import admin
from amsoil.models import *
from modeltranslation.admin import TranslationAdmin
from shop.settings import ADMIN_TEMPLATES_ROOT
from django.forms import ModelChoiceField, ModelForm
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms


# Register your models here.
admin.site.register(Menu)
admin.site.register(MenuItem)
admin.site.register(Category,TranslationAdmin)
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
    readonly_fields = ('date','resend_mail')
    change_form_template = ADMIN_TEMPLATES_ROOT + 'change_order.html'
    fields = ('status','number','date','paymentMethod','shippingMethod',
              'notes','email','phone', 'resend_mail')

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

class MetaInline(admin.TabularInline):
    model = PageMeta
    fields = ('key','value',)
    extra = 1

#class ProductForm(ModelForm):
#    atts = ModelChoiceField(queryset=Attribute.objects.all().order_by('group__name','name'))

class ProductAdmin(admin.ModelAdmin):
    #form = ProductForm
    inlines = (VariationsInline, AttachmentsInline)
    list_display = ['name','mainImage']
    list_editable = ['name']
    filter_horizontal = ('attributes',)
    search_fields = ['name']
    fields = ('name','shortName','description',
              ('attributes'),('mainImage'),
              ('categories','tags'),'is_published')
    #pass

class PostAdmin(admin.ModelAdmin):
    list_display = ['title','author']
    readonly_fields = ('created_at',)
    fields= ('title','url','body','created_at','author','categories','tags')
admin.site.register(Post, PostAdmin)

class ProductVariationAdmin(admin.ModelAdmin):
    model = ProductVariation
    search_fields = ['product']
    list_display = ['product','getAttributesString','price','amount','total_sales','archoil_id']
    list_editable = ['price','amount','archoil_id']

admin.site.register(ProductVariation, ProductVariationAdmin)

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Slider, SliderAdmin)

class ProductsInline(admin.TabularInline):
    model = Product.attributes.through
    extra = 3

# class AttributeAdmin(admin.ModelAdmin):
#     model = Attribute
#     products = forms.ModelMultipleChoiceField(
#         queryset=Product.objects.all(),
#         required=False,
#         widget=FilteredSelectMultiple(
#           verbose_name= 'Produkty',
#           is_stacked=False
#         )
#     )
#     list_display  = ['name']
#     list_editable = ['name']
#     fields = ['name','group', 'products']
#     #inlines = [ProductsInline]


class AttributeAdminForm(forms.ModelForm):
  products = forms.ModelMultipleChoiceField(
    queryset=Product.objects.all(),
    required=False,
    widget=FilteredSelectMultiple(
      verbose_name= 'Produkty',
      is_stacked=False
    )
  )

  class Meta:
    model = Attribute

  def __init__(self, *args, **kwargs):
    super(AttributeAdminForm, self).__init__(*args, **kwargs)

    if self.instance and self.instance.pk:
      self.fields['products'].initial = self.instance.pages.all()

  def save(self, commit=True):
    Attribute = super(AttributeAdminForm, self).save(commit=False)

    if commit:
      Attribute.save()

    if Attribute.pk:
      Attribute.pages = self.cleaned_data['products']
      self.save_m2m()

    return Attribute

class AttributeAdmin(admin.ModelAdmin):
  form = AttributeAdminForm
admin.site.register(Attribute, AttributeAdmin)

admin.site.register(NewsletterReceiver)
admin.site.register(Tag)