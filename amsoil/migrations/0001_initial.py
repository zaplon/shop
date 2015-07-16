# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields
import markitup.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'nazwa')),
                ('file', models.FileField(upload_to=b'/home/jan/PycharmProjects/shop/media/files/', verbose_name=b'plik')),
            ],
            options={
                'verbose_name': 'za\u0142\u0105cznik',
                'verbose_name_plural': 'za\u0142\u0105czniki',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=100, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Atrybut',
                'verbose_name_plural': 'Atrybuty',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AttributeGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('forProductVariations', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Grupa atrybut\xf3w',
                'verbose_name_plural': 'Grupy atrybut\xf3w',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'FI', max_length=20, choices=[(b'FI', b'finished'), (b'TE', b'temporary')])),
                ('json', models.CharField(default=b'{}', max_length=1000)),
            ],
            options={
                'verbose_name': 'Koszyk',
                'verbose_name_plural': 'Koszyki',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CartProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(default=1, verbose_name=b'Ilo\xc5\x9b\xc4\x87')),
                ('price', models.FloatField(default=0, verbose_name=b'Cena')),
                ('cart', models.ForeignKey(related_name=b'cartProducts', to='amsoil.Cart')),
            ],
            options={
                'verbose_name': 'Element koszyka',
                'verbose_name_plural': 'Elementy koszyka',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('name_pl', models.CharField(max_length=100, null=True)),
                ('forProducts', models.BooleanField(default=False)),
                ('image', models.FileField(default=b'', upload_to=b'/home/jan/PycharmProjects/shop/media/images/', blank=True)),
                ('order', models.IntegerField(default=0)),
                ('parent', models.ForeignKey(related_name=b'children', verbose_name=b'rodzic', blank=True, to='amsoil.Category', null=True)),
            ],
            options={
                'verbose_name': 'Kategoria',
                'verbose_name_plural': 'Kategorie',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('NIP', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=100, verbose_name=b'Nazwa')),
                ('address', models.CharField(max_length=150, verbose_name=b'Adres')),
            ],
            options={
                'verbose_name': 'Faktura',
                'verbose_name_plural': 'Faktury',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('url', models.CharField(max_length=30, null=True, blank=True)),
                ('order', models.IntegerField(default=1)),
                ('menu', models.ForeignKey(to='amsoil.Menu')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Method',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=300, null=True, blank=True)),
                ('is_enabled', models.BooleanField(default=True, verbose_name=b'W\xc5\x82\xc4\x85czona')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MethodOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=150)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NewsletterReceiver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=75)),
                ('token', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name': 'Odbiorca newslettera',
                'verbose_name_plural': 'Odbiorcy newsletter\xf3w',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'PE', max_length=20, choices=[(b'PE', b'PENDING'), (b'CA', b'CANCELLED'), (b'FI', b'FINISHED'), (b'FA', b'FAILED')])),
                ('date', models.DateTimeField(auto_now=True, verbose_name=b'Data')),
                ('notes', models.CharField(max_length=200, null=True, verbose_name=b'Uwagi', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name=b'Email')),
                ('number', models.CharField(default=b'', max_length=20, verbose_name=b'Numer zam\xc3\xb3wienia')),
                ('phone', models.CharField(default=0, max_length=15, verbose_name=b'Telefon')),
                ('total', models.FloatField(default=0, verbose_name=b'W sumie')),
                ('token', models.CharField(max_length=30, null=True, blank=True)),
                ('paypalData', models.CharField(max_length=300, null=True, blank=True)),
                ('discount', models.FloatField(default=0, verbose_name=b'Zni\xc5\xbcka')),
                ('cart', models.OneToOneField(related_name=b'order', to='amsoil.Cart')),
            ],
            options={
                'verbose_name': 'Zam\xf3wienie',
                'verbose_name_plural': 'Zam\xf3wienia',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('body', ckeditor.fields.RichTextField(max_length=20000)),
                ('url', models.CharField(default=b'', max_length=100)),
                ('isMain', models.BooleanField(default=0)),
                ('full_width', models.BooleanField(default=0, verbose_name=b'Szeroko\xc5\x9b\xc4\x87 ca\xc5\x82ej strony')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name=b'Utworzono')),
                ('is_published', models.BooleanField(default=True, verbose_name=b'Opublikowane')),
            ],
            options={
                'verbose_name': 'Strona',
                'verbose_name_plural': 'Strony',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PageMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=150)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('method_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='amsoil.Method')),
                ('instructions', models.CharField(max_length=500, null=True, blank=True)),
                ('code', models.CharField(max_length=b'3')),
                ('needsProcessing', models.BooleanField(default=False)),
                ('price', models.FloatField(default=0, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Metoda zap\u0142aty',
                'verbose_name_plural': 'Metody zap\u0142aty',
            },
            bases=('amsoil.method',),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='amsoil.Page')),
                ('author', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Post',
                'verbose_name_plural': 'Posty',
            },
            bases=('amsoil.page',),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='amsoil.Page')),
                ('name', models.CharField(max_length=100)),
                ('shortName', models.CharField(default=b'', max_length=100, null=True, verbose_name=b'Kr\xc3\xb3tka nazwa', blank=True)),
                ('description', ckeditor.fields.RichTextField(default=b'', null=True, verbose_name=b'Opis', blank=True)),
                ('shortDescription', ckeditor.fields.RichTextField(default=b'', max_length=200, null=True, verbose_name=b'Kr\xc3\xb3tki opis', blank=True)),
                ('mainImage', models.FileField(default=None, upload_to=b'images/', verbose_name=b'G\xc5\x82\xc3\xb3wne zdj\xc4\x99cie', blank=True)),
                ('price', models.FloatField(default=0, verbose_name=b'Cena')),
            ],
            options={
                'verbose_name': 'Produkt',
                'verbose_name_plural': 'Produkty',
            },
            bases=('amsoil.page',),
        ),
        migrations.CreateModel(
            name='ProductVariation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('price', models.FloatField(default=0)),
                ('purchase_price', models.FloatField(default=0, verbose_name=b'Cena zakupu')),
                ('image', models.ImageField(null=True, upload_to=b'images/', blank=True)),
                ('amount', models.IntegerField(default=0)),
                ('total_sales', models.IntegerField(default=0)),
                ('added_date', models.DateTimeField(auto_now=True)),
                ('archoil_id', models.IntegerField(null=True, blank=True)),
                ('attributes', models.ManyToManyField(related_name=b'products', to='amsoil.Attribute')),
                ('product', models.ForeignKey(related_name=b'variations', to='amsoil.Product')),
            ],
            options={
                'verbose_name': 'Wariant produktu',
                'verbose_name_plural': 'Warianty produkt\xf3w',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=150, verbose_name=b'Adres')),
                ('postalCode', models.CharField(max_length=6, verbose_name=b'Kod pocztowy')),
                ('phone', models.CharField(max_length=15, verbose_name=b'Telefon')),
                ('name', models.CharField(max_length=100, verbose_name=b'Imi\xc4\x99')),
                ('surname', models.CharField(max_length=100, verbose_name=b'Nazwisko')),
                ('city', models.CharField(max_length=150, verbose_name=b'Miejscowo\xc5\x9b\xc4\x87')),
                ('type', models.CharField(max_length=20, choices=[(b'BU', b'buyer'), (b'RE', b'receiver')])),
                ('order', models.ForeignKey(related_name=b'shipment', blank=True, to='amsoil.Order', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Adres',
                'verbose_name_plural': 'Adresy',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ShippingMethod',
            fields=[
                ('method_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='amsoil.Method')),
                ('needsShipping', models.BooleanField(default=False)),
                ('price', models.FloatField(default=0)),
                ('instructions', models.CharField(max_length=500, null=True, blank=True)),
                ('paymentMethods', models.ManyToManyField(related_name=b'shippingMethods', to='amsoil.PaymentMethod')),
            ],
            options={
                'verbose_name': 'Metoda wysy\u0142ki',
                'verbose_name_plural': 'Metody wysy\u0142ki',
            },
            bases=('amsoil.method',),
        ),
        migrations.CreateModel(
            name='ShopMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=150)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Slide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('text', models.CharField(max_length=500)),
                ('button1Text', models.CharField(default=b'Read more', max_length=50)),
                ('button2Text', models.CharField(max_length=50, null=True, blank=True)),
                ('button1Url', models.CharField(max_length=50, null=True, blank=True)),
                ('image', models.ImageField(upload_to=b'', verbose_name=b'obrazek')),
                ('order', models.IntegerField(default=0, verbose_name=b'Kolejno\xc5\x9b\xc4\x87')),
                ('product', models.ForeignKey(blank=True, to='amsoil.Product', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Slider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tagi',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('body', markitup.fields.MarkupField(no_rendered_field=True)),
                ('_body_rendered', models.TextField(editable=False, blank=True)),
            ],
            options={
                'verbose_name': 'Szablon',
                'verbose_name_plural': 'Szablony',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=150)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='slide',
            name='slider',
            field=models.ForeignKey(related_name=b'slides', to='amsoil.Slider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pagemeta',
            name='page',
            field=models.ForeignKey(to='amsoil.Page'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='attributes',
            field=models.ManyToManyField(related_name=b'pages', null=True, verbose_name=b'Atrybuty', to='amsoil.Attribute', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='categories',
            field=models.ManyToManyField(related_name=b'pages', verbose_name=b'Kategorie', to='amsoil.Category', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='tags',
            field=models.ManyToManyField(related_name=b'pages', verbose_name=b'Tagi', to='amsoil.Tag', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='paymentMethod',
            field=models.ForeignKey(verbose_name=b'Metoda zap\xc5\x82aty', to='amsoil.PaymentMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='shippingMethod',
            field=models.ForeignKey(verbose_name=b'Metoda wysy\xc5\x82ki', to='amsoil.ShippingMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(verbose_name=b'U\xc5\xbcytkownik', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='methodoption',
            name='method',
            field=models.ForeignKey(to='amsoil.Method'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='menuitem',
            name='page',
            field=models.ForeignKey(related_name=b'menuItems', blank=True, to='amsoil.Page', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invoice',
            name='order',
            field=models.OneToOneField(related_name=b'invoice', null=True, blank=True, to='amsoil.Order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invoice',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cartproduct',
            name='product',
            field=models.ForeignKey(verbose_name=b'Produkt', blank=True, to='amsoil.Product', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cartproduct',
            name='productVariation',
            field=models.ForeignKey(related_name=b'cartProduct', default=None, blank=True, to='amsoil.ProductVariation', null=True, verbose_name=b'Wariant produktu'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attribute',
            name='group',
            field=models.ForeignKey(related_name=b'attributes', to='amsoil.AttributeGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attachment',
            name='page',
            field=models.ForeignKey(related_name=b'attachments', to='amsoil.Page'),
            preserve_default=True,
        ),
    ]
