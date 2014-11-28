# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.URLField(unique=True, serialize=False, primary_key=True)),
                ('author', models.CharField(max_length=30)),
                ('video_id', models.CharField(max_length=10)),
                ('text', models.TextField()),
                ('afinn_score', models.FloatField()),
                ('labmt_score', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
