#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'shop.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name
from amsoil.models import Order, Product, ProductVariation
from django.db.models import Sum
from chartit import DataPool, Chart
from django.shortcuts import render_to_response



def orders_by_month():

    q = Order.objects.all().extra({'order_month':'MONTH(date)'})\
            .values('order_month').annotate(count=Sum('total'))

    #Step 1: Create a DataPool with the data we want to retrieve.
    data = \
        DataPool(
           series=
            [{'options': {
               'source': q},
              'terms': [
                'order_month',
                'count'
                ]}
             ])

    #Step 2: Create the Chart object
    cht = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                    'order_month': [
                        'count'
                    ]
                  }}],
            chart_options =
              {'title': {
                   'text': 'Suma zamówień w miesiącach'},
               'yAxis': {
                    'title': {
                       'text': 'Sprzedaż'}},
               'xAxis': {
                    'title': {
                       'text': 'Miesiąc'}}})

    #Step 3: Send the chart object to the template.
    return cht


def top_sales():

    q = ProductVariation.objects.all().order_by('-total_sales')[0:10]

    #Step 1: Create a DataPool with the data we want to retrieve.
    data = \
        DataPool(
           series=
            [{'options': {
               'source': q},
              'terms': [
                'product__name',
                'total_sales'
                ]}
             ])

    #Step 2: Create the Chart object
    cht = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms':{
                    'product__name': [
                        'total_sales'
                    ]
                  }}],
            chart_options =
              {'title': {
                   'text': 'Najlepiej sprzedające się produkty'},
               'yAxis': {
                    'title': {
                       'text': 'Sprzedaż'}},
               'xAxis': {
                    'title': {
                       'text': 'Produkt'}}})

    #Step 3: Send the chart object to the template.
    return cht


class Charts(modules.DashboardModule):
    template = 'admin/charts_module.html'
    def init_with_context(self, context):
        if self._initialized:
            return

        self.charts = [ orders_by_month(), top_sales() ]
        self._initialized = True

    def is_empty(self):
        pass

class SalesModule(modules.DashboardModule):
    template = 'admin/sales_module.html'

    def init_with_context(self, context):
        if self._initialized:
            return

        orders = Order.objects.all().order_by('-date')
        #self.orders_per_month = orders.extra({'order_month':'MONTH(date)'})\
        #    .values('order_month').annotate(count=Sum('total'))

        self.orders = orders[0:5]
        self._initialized = True

    def is_empty(self):
        pass

class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """
    template = 'admin/dashboard.html'
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        
        # append a group for "Administration" & "Applications"
        self.children.append(modules.Group(
            _('Group: Administration & Applications'),
            column=1,
            collapsible=True,
            children = [
                modules.AppList(
                    _('Administration'),
                    column=1,
                    collapsible=False,
                    models=('django.contrib.*',),
                ),
                modules.AppList(
                    _('Applications'),
                    column=1,
                    css_classes=('collapse closed',),
                    exclude=('django.contrib.*',),
                )
            ]
        ))
        
        # append an app list module for "Applications"
        #self.children.append(modules.AppList(
        #    _('AppList: Applications'),
        #    collapsible=True,
        #    column=1,
        #    css_classes=('collapse closed',),
        #    exclude=('django.contrib.*',),
        #))
        
        # append an app list module for "Administration"
        #self.children.append(modules.ModelList(
        #    _('ModelList: Administration'),
        #    column=1,
        #    collapsible=False,
        #    models=('django.contrib.*',),
        #))
        
        # append another link list module for "support".
        # self.children.append(modules.LinkList(
        #     _('Media Management'),
        #     column=2,
        #     children=[
        #         {
        #             'title': _('FileBrowser'),
        #             'url': '/admin/filebrowser/browse/',
        #             'external': False,
        #         },
        #     ]
        # ))

        self.children.append(Charts(
            'Statystyki',
            column=2,
        ))

        self.children.append(SalesModule(
            'Ostatnie zamówienia',
            column=2,
        ))

        # append another link list module for "support".
        # self.children.append(modules.LinkList(
        #     _('Support'),
        #     column=2,
        #     children=[
        #         {
        #             'title': _('Django Documentation'),
        #             'url': 'http://docs.djangoproject.com/',
        #             'external': True,
        #         },
        #         {
        #             'title': _('Grappelli Documentation'),
        #             'url': 'http://packages.python.org/django-grappelli/',
        #             'external': True,
        #         },
        #         {
        #             'title': _('Grappelli Google-Code'),
        #             'url': 'http://code.google.com/p/django-grappelli/',
        #             'external': True,
        #         },
        #     ]
        # ))
        #
        # # append a feed module
        # self.children.append(modules.Feed(
        #     _('Latest Django News'),
        #     column=2,
        #     feed_url='http://www.djangoproject.com/rss/weblog/',
        #     limit=5
        # ))
        
        # append a recent actions module
        # self.children.append(modules.RecentActions(
        #     _('Recent Actions'),
        #     limit=5,
        #     collapsible=False,
        #     column=2,
        # ))


