# Generated by Django 4.2.6 on 2023-10-28 10:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0014_merge_20231027_2327'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='project',
            name='start_time_check',
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.CheckConstraint(check=models.Q(('start_time__gte', datetime.date(2023, 10, 28))), name='start_time_check'),
        ),
    ]
