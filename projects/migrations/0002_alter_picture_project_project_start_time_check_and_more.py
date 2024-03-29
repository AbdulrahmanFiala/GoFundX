# Generated by Django 4.2.6 on 2023-10-26 07:53

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='projects.project'),
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.CheckConstraint(check=models.Q(('start_time__gte', datetime.datetime(2023, 10, 26, 7, 53, 27, 851303, tzinfo=datetime.timezone.utc))), name='start_time_check'),
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.CheckConstraint(check=models.Q(('end_time__gte', models.F('start_time'))), name='end_time_check'),
        ),
    ]
