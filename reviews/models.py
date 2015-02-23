#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from shop.settings import REVIEWS_SETTINGS
# Create your models here.

class Opinion(models.Model):
    class Meta:
        verbose_name = 'Opinia'
        verbose_name_plural = 'Opinie'
    service = models.ForeignKey(REVIEWS_SETTINGS['model'], blank=True, null=True)
    content = models.CharField(max_length=1000, verbose_name='Treść')
    added_by = models.CharField(max_length=100, verbose_name='Dodane przez')
    added_at = models.DateTimeField(auto_now=True, verbose_name='Data dodania')
    def __unicode__(self):
        return self.added_by

# oceny
class Mark(models.Model):
    service = models.ForeignKey(REVIEWS_SETTINGS['model'])
    mark = models.IntegerField()
    added_by = models.CharField(max_length=100)
    added_at = models.DateTimeField(auto_now=True)