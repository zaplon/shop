# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('amsoil', '0003_auto_20150221_1142'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mark', models.IntegerField()),
                ('added_by', models.CharField(max_length=100)),
                ('added_at', models.DateTimeField(auto_now=True)),
                ('service', models.ForeignKey(to='amsoil.Product')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Opinion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(max_length=1000)),
                ('added_by', models.CharField(max_length=100)),
                ('added_at', models.DateTimeField(auto_now=True)),
                ('service', models.ForeignKey(to='amsoil.Product')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
