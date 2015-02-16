#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from amsoil.models import PaymentMethod, ShippingMethod, Page, Slider

class Command(BaseCommand):

  def makeMethods(self):
      p1 = PaymentMethod(name='Gotówka', instructions='Zapłać gotówką przy odbiorze zamówienia', code='got')
      p2 = PaymentMethod(name='Przelew bankowy', instructions='Zapłać za pomocą przelewu bankowego', code='prz')
      p3 = PaymentMethod(name='PayPal', instructions='Zapłać przy pomocy PayPal przy użyciu swojego konta'
                                                'lub karty', code='pp', needsProcessing=True)
      p1.save()
      p2.save()
      p3.save()

      s1 = ShippingMethod(name='Odbiór osobisty')
      s1.save()
      s1.paymentMethods.add(p1)
      s1.paymentMethods.add(p2)
      s1.paymentMethods.add(p3)
      s2 = ShippingMethod(name='Przesyłka kurierska', needsShipping=True)
      s2.save()
      s2.paymentMethods.add(p1)
      s2.paymentMethods.add(p2)
      s2.paymentMethods.add(p3)
      s3 = ShippingMethod(name='Przesyłka kurierska pobraniowa', price='15', needsShipping=True)
      s3.save()
      s3.paymentMethods.add(p1)


  def makePages(self):
      p1 = Page(title='Kontakt',body='', url='Kontakt')
      p1.save()
      p2 = Page(title='Regulamin sklepu internetowego www.najlepszysyntetyk.pl', body='', url='Regulamin')
      self.makeMethods()

  def makeSlider(self):
      s = Slider(name='main')
      s.save()

  def handle(self,*args,**options):
      self.makeMethods()
      self.makePages()
      self.makeSlider()
