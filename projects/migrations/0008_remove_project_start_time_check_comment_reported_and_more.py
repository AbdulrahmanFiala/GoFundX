# Generated by Django 4.2.6 on 2023-10-27 17:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_picture_is_main'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='project',
            name='start_time_check',
        ),
        migrations.AddField(
            model_name='comment',
            name='reported',
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.CheckConstraint(check=models.Q(('start_time__gte', datetime.date(2023, 10, 27))), name='start_time_check'),
        ),
    ]
