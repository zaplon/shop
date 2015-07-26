# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from amsoil.models import Order


class Command(BaseCommand):

  def handle(self,*args,**options):
    for o in Order.objects.all():
        o.get_income()
        o.save()