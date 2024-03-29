# Generated by Django 4.2.6 on 2023-10-26 08:47

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0002_alter_picture_project_project_start_time_check_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
            ],
        ),
        migrations.RemoveConstraint(
            model_name='project',
            name='start_time_check',
        ),
        migrations.AddField(
            model_name='comment',
            name='reports_num',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='project',
            name='reports_num',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='project',
            name='total_raised',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='project',
            name='end_time',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='project',
            name='start_time',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='project',
            name='total_target',
            field=models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(250000)]),
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.CheckConstraint(check=models.Q(('start_time__gte', datetime.datetime(2023, 10, 26, 8, 47, 22, 192252, tzinfo=datetime.timezone.utc))), name='start_time_check'),
        ),
        migrations.AddField(
            model_name='rating',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project'),
        ),
        migrations.AddField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
