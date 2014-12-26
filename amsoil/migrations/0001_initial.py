# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to=b'/home/jan/PycharmProjects/shop/media/files/')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=100)),
            ],
            options={
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
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=20, choices=[(b'FI', b'finished'), (b'TE', b'temporary')])),
                ('json', models.CharField(max_length=1000)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CartProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(default=1)),
                ('price', models.FloatField(default=0)),
                ('cart', models.ForeignKey(related_name=b'cartProducts', to='amsoil.Cart')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('name_pl', models.CharField(max_length=100, null=True)),
                ('name_en', models.CharField(max_length=100, null=True)),
                ('forProducts', models.BooleanField(default=False)),
                ('image', models.FileField(default=b'', upload_to=b'/home/jan/PycharmProjects/shop/media/images/', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('NIP', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=150)),
            ],
            options={
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
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'PE', max_length=20, choices=[(b'PE', b'pending'), (b'CA', b'cancelled'), (b'FI', b'finished')])),
                ('date', models.DateTimeField()),
                ('notes', models.CharField(max_length=200, null=True, blank=True)),
                ('email', models.EmailField(max_length=75)),
                ('cart', models.ForeignKey(to='amsoil.Cart')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('body', ckeditor.fields.RichTextField(max_length=20000)),
                ('isMain', models.BooleanField(default=0)),
            ],
            options={
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
            },
            bases=('amsoil.method',),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='amsoil.Page')),
                ('name', models.CharField(max_length=100)),
                ('shortName', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('description', ckeditor.fields.RichTextField(default=b'', max_length=2000, null=True, blank=True)),
                ('shortDescription', ckeditor.fields.RichTextField(default=b'', max_length=200, null=True, blank=True)),
                ('mainImage', models.FileField(default=None, upload_to=b'images/', blank=True)),
                ('price', models.FloatField(default=0)),
            ],
            options={
            },
            bases=('amsoil.page',),
        ),
        migrations.CreateModel(
            name='ProductVariation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('price', models.FloatField(default=0)),
                ('image', models.ImageField(upload_to=b'images/')),
                ('amount', models.IntegerField(default=0)),
                ('attributes', models.ManyToManyField(related_name=b'products', to='amsoil.Attribute')),
                ('product', models.ForeignKey(related_name=b'variations', to='amsoil.Product')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=150)),
                ('postalCode', models.CharField(max_length=6)),
                ('phone', models.CharField(max_length=15)),
                ('name', models.CharField(max_length=100)),
                ('surname', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=20, choices=[(b'BU', b'buyer'), (b'RE', b'receiver')])),
                ('order', models.ForeignKey(related_name=b'shipment', to='amsoil.Order')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ShippingMethod',
            fields=[
                ('method_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='amsoil.Method')),
                ('needsShipping', models.BooleanField(default=False)),
                ('price', models.FloatField(default=0)),
                ('paymentMethods', models.ManyToManyField(related_name=b'shippingMethods', to='amsoil.PaymentMethod')),
            ],
            options={
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
                ('image', models.URLField(null=True, blank=True)),
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
            field=models.ForeignKey(to='amsoil.Slider'),
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
            name='categories',
            field=models.ManyToManyField(related_name=b'pages', to='amsoil.Category', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='tags',
            field=models.ManyToManyField(related_name=b'pages', to='amsoil.Tag', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='paymentMethod',
            field=models.ForeignKey(to='amsoil.PaymentMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='shippingMethod',
            field=models.ForeignKey(to='amsoil.ShippingMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
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
            field=models.ForeignKey(blank=True, to='amsoil.Order', null=True),
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
            field=models.ForeignKey(blank=True, to='amsoil.Product', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cartproduct',
            name='productVariation',
            field=models.ForeignKey(default=None, blank=True, to='amsoil.ProductVariation', null=True),
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
