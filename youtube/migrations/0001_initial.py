# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.CharField(max_length=20, unique=True, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.URLField(unique=True, serialize=False, primary_key=True)),
                ('author', models.CharField(max_length=30)),
                ('text', models.TextField()),
                ('date', models.DateTimeField()),
                ('afinn_score', models.FloatField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.CharField(max_length=20, unique=True, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=30)),
                ('rating', models.FloatField(blank=True)),
                ('date', models.DateTimeField()),
                ('image', models.URLField()),
                ('view_count', models.IntegerField()),
                ('category', models.ForeignKey(to='youtube.Category')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='comment',
            name='video',
            field=models.ForeignKey(to='youtube.Video'),
            preserve_default=True,
        ),
    ]
