# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portmonitor', '0012_auto_20160926_1116'),
    ]

    operations = [
        migrations.CreateModel(
            name='checktask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project_id', models.IntegerField()),
                ('domain', models.CharField(max_length=100)),
                ('module', models.CharField(max_length=100)),
                ('frequency', models.IntegerField()),
                ('lastcheck', models.IntegerField(default=0)),
            ],
        ),
    ]
