from django.conf.urls import patterns, include, url
from django.contrib import admin
from amsoil import views, mails
from shop.settings import MEDIA_URL, MEDIA_ROOT
from django.conf.urls.static import static
from authentication.views import loginView, logoutView, register

from amsoil.views import ProductVariationViewSet, OrderViewSet, ClientViewSet
from rest_framework.routers import DefaultRouter
from reviews.views import MarkViewSet, OpinionViewSet, opinions_view

router = DefaultRouter()
router.register(r'productVariations', ProductVariationViewSet)
router.register(r'marks', MarkViewSet)
router.register(r'opinions', OpinionViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'clients', ClientViewSet)

urlpatterns = patterns('',

    #admin-toos
    #url(r'^admin_tools/', include('admin_tools.urls')),

    #api
    url(r'api/', include(router.urls)),
    url(r'api/products/',views.ShopProductListView.as_view(), name='api-product-list'),

    url(r'^najnowsze-informacje/(?P<url>.*)/$', views.postView, name='post'),
    url(r'^najnowsze-informacje/', views.postsView, name='posts'),
    url(r'^opinie/', opinions_view, name='opinions'),
    url(r'^formularz-przeslany/', views.form_submitted, name='form-submitted'),

    url(r'^$', views.home, name='home'),
    url(r'^sklep/kategoria/(?P<category>.*)/', views.shop, name='shopCategory'),
    url(r'^sklep/produkt/(?P<name>.*)/$', views.singleProduct, name='singleProduct'),
    url(r'^sklep/', views.shop, name='shop'),
    url(r'^page/(?P<id>[0-9]+)/$', views.page, name='page'),
    url(r'^zamowienie/', views.checkout, name='checkout'),
    url(r'^zamowienie-przetworzone/(?P<pk>[0-9]+)/$', views.checkout_processed, name='checkout-processed'),
    url(r'^konto/', views.account, name='account'),
    url(r'^koszyk/', views.cart, name='cart'),
    url(r'^takeCart/', views.takeCart, name='takeCart'),
    url(r'^getOrderOptions/', views.getOrderOptions, name='checkoutOptions'),

    url(r'', include('getpaid.urls')),

    url(r'^test/(?P<pk>\d+)/$', views.OrderView.as_view(), name='test'),

    url(r'^authentication/', include('authentication.urls', namespace='authentication')),
    url(r'^',include('password_reset.urls')),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^miniCart/', views.minicart, name='minicart'),
    url(r'^produkty/', views.ProductListView.as_view(), name='product-list'),

    url(r'^login/', loginView, name='login'),
    url(r'^logout/', logoutView, name='logout'),
    url(r'^zarejestruj/', register, name='register'),

    url(r'^addToCart/', views.addToCart, name='addToCart'),
    url(r'^removeFromCart/', views.removeFromCart, name='removeFromCart'),
    url(r'^updateCart/', views.updateCart, name='updateCart'),

    url(r'^quickContact/', views.quickContact, name='contact'),
    url(r'^szukaj/', views.search, name='search'),

    url(r'^newsletter-receiver/', views.NewsletterReceiverListCreateView.as_view(), name='newsletter-receiver'),
    url(r'^newsletter-rejestracja/', views.newsletter_register, name='newsletter-register'),

    url(r'^markitup/', include('markitup.urls')),

    #przesylanie z sklep.archoil.pl
    url(r'^archoil_order/', views.archoil_order, name='archoil_order'),

    url(r'^resend_order/', mails.resend_order, name='resend-mail'),

    url(r'^robots.txt', views.robots, name='robots'),

    url(r'^accept-cookies/', views.accept_cookies, name='accept-cookies'),
    url(r'^ifirma/', views.ifirma, name='ifirma'),

    url(r'^allegro/(?P<id>[0-9]+)/$', views.allegro, name='allegro'),
    url(r'^(?P<title>.*)/$', views.page, name='page'),

)

urlpatterns = urlpatterns + static(MEDIA_URL, document_root=MEDIA_ROOT)
