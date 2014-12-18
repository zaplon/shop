from django.conf.urls import patterns, include, url
from django.contrib import admin
from amsoil import views
from amsoil.models import Product
from shop.settings import MEDIA_URL, MEDIA_ROOT
from django.conf.urls.static import static

urlpatterns = patterns('',
    # Examples:

    url(r'^$', views.home, name='home'),
    url(r'^shop/product/(?P<id>[0-9]+)/$', views.singleProduct, name='singleProduct'),
    url(r'^page/(?P<id>[0-9]+)/$', views.page, name='page'),
    url(r'^shop/', views.shop, name='shop'),
    url(r'^checkout/', views.checkout, name='checkout'),
    url(r'^account/', views.account, name='account'),
    url(r'^cart/', views.cart, name='cart'),
    url(r'^takeCart/', views.takeCart, name='takeCart'),
    url(r'^getOrderOptions/', views.getOrderOptions, name='checkoutOptions'),

    # url(r'^blog/', include('blog.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^miniCart/', views.minicart, name='minicart'),
    url(r'^products/', views.ProductListView.as_view(model=Product), name='product-list'),
    #url(r'^carts/', views.CartDetail.as_view()),

    url(r'^login/', views.loginView, name='login'),
    url(r'^logout/', views.logoutView, name='logout'),
    url(r'^register/', views.register, name='register'),

    url(r'^addToCart/', views.addToCart, name='addToCart'),
    url(r'^removeFromCart/', views.removeFromCart, name='removeFromCart'),
    url(r'^updateCart/', views.updateCart, name='updateCart'),

    url(r'^quickContact/', views.quickContact, name='contact'),
    url(r'^search/', views.search, name='search'),

)

urlpatterns = urlpatterns + static(MEDIA_URL, document_root=MEDIA_ROOT)