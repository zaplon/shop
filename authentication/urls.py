from django.conf.urls import url

from authentication import views

urlpatterns = [

    url(r'^password-reset/$', views.password_reset, name='password_reset'),
    url(r'^password-reset-done/$', views.password_reset_done, name='password_reset_done'),

]