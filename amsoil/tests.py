#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django.test import TestCase
from models import Product, ProductVariation, Attribute, AttributeGroup
from payments import paypal_step_1, paypal_step_2
# Create your tests here.

class AttributeGroupTestCase(TestCase):
    def setUp(self):
        ag1 = AttributeGroup(name='Lepkość')
        ag1.save()
        ag2 = AttributeGroup(name='Opakowanie', for_products=True)
        ag2.save()
    def test_can_find_attribute_group(self):
        AttributeGroup.objects.get(name='Opakowanie')

class AttributeTestCase(TestCase):
    def setUp(self):
        a1 = Attribute(group=AttributeGroup.get(name='Opakowanie'), name='1L')
        a1.save()


class ProductVariationTestCase(TestCase):
    def setUp(self):
        pv = ProductVariation(price=30)
        pv.attributes.add(Attribute.objects.get(name='1L'))
        pv.save()

class ProductTestCase(TestCase):
    def setUp(self):
        p = Product(name='Olej silnikowy')
        p.variations.add(ProductVariation.objects.get(attributes__name='1L'))
        p.save()


class OrderTestCast(TestCase):
    def test_can_checkout(self):
        pass


class paymentTestCase(TestCase):

    def test_can_make_PayPal_payment(self):
        pass
