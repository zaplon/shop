# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('amsoil', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDiscount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField(default=0, verbose_name=b'Wysoko\xc5\x9b\xc4\x87 zni\xc5\xbcki w %')),
                ('attribute', models.ForeignKey(verbose_name=b'Atrybut', blank=True, to='amsoil.Attribute', null=True)),
                ('product', models.ForeignKey(verbose_name=b'Produkt', blank=True, to='amsoil.ProductVariation', null=True)),
                ('user', models.ForeignKey(related_name=b'discounts', verbose_name=b'U\xc5\xbcytkownik', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='order',
            name='mail_sended',
            field=models.BooleanField(default=False, verbose_name=b'Mail przes\xc5\x82any'),
            preserve_default=True,
        ),
    ]
