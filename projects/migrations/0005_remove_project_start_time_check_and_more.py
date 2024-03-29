# Generated by Django 4.2.6 on 2023-10-26 08:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_remove_project_start_time_check_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='project',
            name='start_time_check',
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.CheckConstraint(check=models.Q(('start_time__gte', datetime.date(2023, 10, 26))), name='start_time_check'),
        ),
    ]
