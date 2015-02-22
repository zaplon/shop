from django.db import models
from shop.settings import REVIEWS_SETTINGS
# Create your models here.

class Opinion(models.Model):
    service = models.ForeignKey(REVIEWS_SETTINGS['model'])
    content = models.CharField(max_length=1000)
    added_by = models.CharField(max_length=100)
    added_at = models.DateTimeField(auto_now=True)


# oceny
class Mark(models.Model):
    service = models.ForeignKey(REVIEWS_SETTINGS['model'])
    mark = models.IntegerField()
    added_by = models.CharField(max_length=100)
    added_at = models.DateTimeField(auto_now=True)