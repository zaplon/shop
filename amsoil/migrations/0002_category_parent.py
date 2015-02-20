# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('amsoil', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(related_name=b'children', verbose_name=b'rodzic', blank=True, to='amsoil.Category', null=True),
            preserve_default=True,
        ),
    ]