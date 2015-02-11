from django.conf.urls import patterns, include, url
from django.contrib import admin
from amsoil import views
from amsoil.models import Product
from shop.settings import MEDIA_URL, MEDIA_ROOT
from django.conf.urls.static import static
from authentication.views import loginView, logoutView, register

urlpatterns = patterns('',
    # Examples:

    url(r'^$', views.home, name='home'),
    url(r'^sklep/kategoria/(?P<category>.*)/', views.shop, name='shopCategory'),
    url(r'^sklep/produkt/(?P<name>.*)/$', views.singleProduct, name='singleProduct'),
    url(r'^sklep/', views.shop, name='shop'),
    url(r'^page/(?P<id>[0-9]+)/$', views.page, name='page'),
    url(r'^zamowienie/', views.checkout, name='checkout'),
    url(r'^konto/', views.account, name='account'),
    url(r'^koszyk/', views.cart, name='cart'),
    url(r'^takeCart/', views.takeCart, name='takeCart'),
    url(r'^getOrderOptions/', views.getOrderOptions, name='checkoutOptions'),

    # url(r'^blog/', include('blog.urls')),

    url(r'^authentication/', include('authentication.urls', namespace='authentication')),
    url(r'^',include('password_reset.urls')),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^miniCart/', views.minicart, name='minicart'),
    url(r'^produkty/', views.ProductListView.as_view(model=Product), name='product-list'),
    #url(r'^carts/', views.CartDetail.as_view()),

    url(r'^login/', loginView, name='login'),
    url(r'^logout/', logoutView, name='logout'),
    url(r'^zarejestruj/', register, name='register'),

    url(r'^addToCart/', views.addToCart, name='addToCart'),
    url(r'^removeFromCart/', views.removeFromCart, name='removeFromCart'),
    url(r'^updateCart/', views.updateCart, name='updateCart'),

    url(r'^quickContact/', views.quickContact, name='contact'),
    url(r'^szukaj/', views.search, name='search'),

    url(r'^newsletter-receiver/', views.NewsletterReceiverListCreateView.as_view(), name='newsletter-receiver'),


    url(r'^(?P<title>.*)/$', views.page, name='page'),


    #(r'^accounts/', include('registration.backends.default.urls')),

)

urlpatterns = urlpatterns + static(MEDIA_URL, document_root=MEDIA_ROOT)