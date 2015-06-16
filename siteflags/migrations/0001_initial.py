# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.TextField(verbose_name='Note', blank=True)),
                ('status', models.IntegerField(db_index=True, null=True, verbose_name='Status', blank=True)),
                ('time_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('object_id', models.PositiveIntegerField(verbose_name='Object ID', db_index=True)),
                ('content_type', models.ForeignKey(related_name='siteflags_flag_flags', verbose_name='Content type', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(related_name='flag_users', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Flag',
                'verbose_name_plural': 'Flags',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='flag',
            unique_together=set([('content_type', 'object_id', 'user', 'status')]),
        ),
    ]
