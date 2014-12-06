# -*- coding: utf-8 -*-

import MySQLdb, sqlsoup, json, datetime
from MySQLdb.cursors import DictCursor
from sqlalchemy import or_, and_, desc
from phpserialize import *
from xml.sax.saxutils import escape
import urllib, os

from django.core.management.base import BaseCommand, CommandError
from amsoil.models import Product, ProductVariation, Category, AttributeGroup, Attribute


class prices:
    story = []
    pageNr = 1
    date = datetime.date.today().strftime('%d-%m-%y')
    uploads = '/var/www/amsoil2/public_html/wp-content/uploads/'
    images_url = 'http://www.najlepszysyntetyk.pl/wp-content/uploads/'

    def doUsers(self):
        metas  =['first_name', 'last_name','nickname','billing_first_name','billing_last_name',
                 'billing_address_1','billing_address_2','billing_city','billing_postcode',
                 'billing_phone','billing_email']
        db = sqlsoup.SQLSoup('mysql://root:sadyba88@localhost/amsoil?charset=utf8')
        users = db.wp_users.all()


    def doPrices(self):    

        db = sqlsoup.SQLSoup('mysql://root:sadyba88@localhost/amsoil?charset=utf8')
    
        where = (db.wp_posts.post_type =='product')
        posts = db.wp_posts.filter(where).all()
        
        objs = []
            
        #pola potrzebne m._price, m._product_attributes, m.portfolio_excerpt, _thumbnail_id
        keys = [ '_price', 'catalogue_desc', '_thumbnail_id', '_product_attributes' ]
        #vKeys = ['attribute_opakowanie', '_price','attribute_zestaw-promocyjny', 'attribute_zestaw', 'attribute_przeznaczenie']
        #types = ['attribute_opakowanie', 'attribute_zestaw-promocyjny', 'attribute_zestaw', 'attribute_przeznaczenie']
        for p in posts:
            #postmeta post
            obj = { 'content': p.post_content, 'name': p.post_title, 'vars': { 'price': [], 'name': [], 'np':[] }, 'catalogue_desc':'', 'post_excerpt':escape(p.post_excerpt) }
            pms = db.wp_postmeta.filter( db.wp_postmeta.post_id == p.ID  )
            for pm in pms:
                if pm.meta_key in keys :
                    obj[pm.meta_key] = pm.meta_value
            obj['_product_attributes'] = loads(obj['_product_attributes'])
            isVar = False
            attr = []
            vals = []
            for a in obj['_product_attributes']:
                attr.append('attribute_'+a)
                if obj['_product_attributes'][a]['is_variation']:
                    isVar = True
                    vals = vals + obj['_product_attributes'][a]['value'].split(' | ')
            #print obj['_product_attributes']       
            if isVar:
                q = """
                        SELECT post.ID, meta.meta_key, meta.meta_value 
                        FROM wp_posts post
                        INNER JOIN wp_postmeta meta ON post.ID = meta.post_id
                        WHERE meta.meta_key = '_price' AND post.post_type = 'product_variation' AND post.post_parent =
                        """ + str(p.ID) + ' ORDER BY meta.meta_value'
                rows = db.execute(q).fetchall() 
                for row in rows:
                    i = 0
                    pvms = db.wp_postmeta.filter(db.wp_postmeta.post_id == row[0]).all()
                    for pvm in pvms:
                        if pvm.meta_key == '_price':
                            obj['vars']['price'].append(pvm.meta_value)    
                        if pvm.meta_key in attr :
                            if i < len(vals):
                                obj['vars']['name'].append(vals[i])
                            else:
                                obj['vars']['name'].append(pvm.meta_value.replace('-',' '))
                    try:            
                        obj['vars']['np'].append(str(obj['vars']['name'][-1]) + '/' + str(obj['vars']['price'][-1]+'zł'))
                    except:
                        obj['vars']['np'].append('')  
                    i = i + 1          
            elif len(attr) > 0:
                #opakowania
                #print obj
                attr2 = []
                for a in attr:
                    attr2.append("'"+str(a.replace('attribute_',''))+"'")
                q = """
                    SELECT ter.name FROM `wp_term_relationships` rel 
                    INNER JOIN wp_term_taxonomy tax ON rel.term_taxonomy_id = tax.term_taxonomy_id
                    INNER JOIN wp_terms ter ON ter.term_id = tax.term_id 
                    WHERE tax.taxonomy IN ("""+' ,'.join(attr2)+""") AND rel.object_id = """ + str(p.ID)
                sizes = db.execute(q).fetchall()
                #print sizes
                obj['vars']['price'].append(obj['_price'])
                try:
                    obj['vars']['name'].append(sizes[0][0])
                except:
                    #print obj['_product_attributes']
                    obj['vars']['name'].append('')    
                #obj['vars']['np'].append( str(price[0].meta_value) + '/' + obj['vars']['name'] )
            
            else:
                obj['vars']['name'].append('b')
                obj['vars']['price'].append('b')
            
            #kategoria
            q = """
                SELECT ter.name FROM `wp_term_relationships` rel 
                INNER JOIN wp_term_taxonomy tax ON rel.term_taxonomy_id = tax.term_taxonomy_id
                INNER JOIN wp_terms ter ON ter.term_id = tax.term_id 
                WHERE tax.taxonomy = 'product_cat' AND rel.object_id = """ + str(p.ID)
            cat = db.execute(q).fetchall()
            obj['cat'] = str(cat[0][0].encode('utf8'))
            
            src = db.wp_postmeta.filter(and_( db.wp_postmeta.post_id == obj['_thumbnail_id'], db.wp_postmeta.meta_key == '_wp_attached_file' ) ).all()
            obj['_thumbnail_id'] = src[0].meta_value
               
            objs.append(obj)         
                
        #print objs
        cats = {}
        
        for o in objs:
            if o['cat'] in cats:
                cats[o['cat']].append( o )
            else:
                cats[o['cat']] = []
                cats[o['cat']].append( o )
                    
        #print cats

        ag = AttributeGroup(forProductVariations = True, name = 'opakowanie')
        ag.save()

        for cat in cats:
            c = Category(name = cat, forProducts = True)
            c.save()
            for o in cats[cat]:
                print self.images_url+o['_thumbnail_id']
                ext = o['_thumbnail_id'].split('.')[1]
                name = datetime.datetime.now().strftime('%s')+'.'+ext
                name = name
                urllib.urlretrieve(self.images_url+o['_thumbnail_id'], 'media/images/' + name)
                p = Product(description = o['content'], shortDescription = o['post_excerpt'], name = o['name'],
                            mainImage = 'images/'+name)
                p.save()
                p.categories.add(c)
                p.save()
                #os.remove(name)
                i = 0
                for v in o['vars']['price']:
                    try:
                        a = Attribute.objects.get(name = o['vars']['name'][i])
                    except:
                        a = Attribute(name = o['vars']['name'][i], group = ag)
                        a.save()
                    #print o['vars']['price'][i]
                    try:
                        pv = ProductVariation(product = p, price = float(o['vars']['price'][i]))
                        pv.save()
                        pv.attributes.add(a)
                        pv.save()
                    except:
                        pass
                    i = i + 1

class Command(BaseCommand):

  def handle(self,*args,**options):
    p = prices()
    p.doPrices()
