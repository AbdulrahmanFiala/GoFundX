# Generated by Django 4.2.6 on 2023-10-26 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_project_is_featured_alter_picture_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='picture',
            name='is_main',
            field=models.BooleanField(default=False),
        ),
    ]
