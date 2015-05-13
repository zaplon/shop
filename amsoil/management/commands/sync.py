# -*- coding: utf-8 -*-

import MySQLdb, sqlsoup, json, datetime
from MySQLdb.cursors import DictCursor
from sqlalchemy import or_, and_, desc
from phpserialize import *
from xml.sax.saxutils import escape
import urllib, os

from django.core.management.base import BaseCommand, CommandError
from amsoil.models import Product, ProductVariation, dictfetchall


class sync:
    def __init__(self):
        self.archoil = sqlsoup.SQLSoup('mysql://archoilpl:5fa9b107-4dd4-478f-ad51-67cd7a769fe1@archoil.pl/archoilpl?charset=utf8')
    def do_sync(self):
        data = {}
        query = """
            SELECT m.meta_value as quantity, p.id FROM arc_postmeta m
            INNER JOIN arc_posts p ON p.id = m.post_id
            WHERE (p.post_type = 'product' OR p.post_type = 'product_variation') AND m.meta_key = '_stock'
        """
        rows = self.archoil.execute(query).fetchall()
        dict = ['quantity', 'id']
        new_rows = []
        #row_to_dict = lambda row: dict((col, getattr(row, col)) for col in row.__table__.columns.keys())

        for r in rows:
            i = 0
            new_row = {}
            for rr in r:
                new_row[dict[i]] = rr
                i = i + 1
            new_rows.append(new_row)
        rows = new_rows
        for r in rows:
            try:
                pv = ProductVariation.objects.get(archoil_id=r['id'])

                quantity = int(r['quantity'])
                print str(quantity) + ' ' + str(pv.amount)
                if pv.amount > quantity:
                    print 'ns more'
                    pv.amount = quantity
                    pv.save()
                elif pv.amount < quantity:
                    print 'archoil more'
                    q = 'SELECT * FROM arc_postmeta meta WHERE meta.meta_key="_stock" AND meta.post_id=%s' % pv.archoil_id
                    res = self.archoil.execute(q).fetchall()
                    q = """
                        UPDATE arc_postmeta
                        SET meta_value = %s
                        WHERE meta_key='_stock' AND post_id='%i'
                    """ % (pv.amount, pv.archoil_id)
                    self.archoil.execute(q)
                    self.archoil.commit()
                    print 'end'
                else:
                    print 'the same'
            except:
                #print 'no match'
                continue

class Command(BaseCommand):

  def handle(self,*args,**options):
    s = sync()
    s.do_sync()
