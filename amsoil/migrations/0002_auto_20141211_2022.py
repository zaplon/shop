# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('amsoil', '0001_initial'),
    ]

    operations = [
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
        migrations.AddField(
            model_name='slide',
            name='slider',
            field=models.ForeignKey(to='amsoil.Slider'),
            preserve_default=True,
        ),
    ]
