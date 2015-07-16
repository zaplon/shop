# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('amsoil', '0002_auto_20150713_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdiscount',
            name='group',
            field=models.ForeignKey(related_name=b'discounts', verbose_name=b'Grupa u\xc5\xbcytkownik\xc3\xb3w', blank=True, to='auth.Group', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userdiscount',
            name='user',
            field=models.ForeignKey(related_name=b'discounts', verbose_name=b'U\xc5\xbcytkownik', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
