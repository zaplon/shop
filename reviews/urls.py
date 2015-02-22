from django.conf.urls import patterns, include, url
from rest_framework.routers import DefaultRouter
from .views import MarkViewSet, OpinionViewSet
from shop.urls import router

#router.register(r'marks', MarkViewSet)
#router.register(r'opinions', OpinionViewSet)

#urlpatterns = patterns(url(r'', include(router.urls)))