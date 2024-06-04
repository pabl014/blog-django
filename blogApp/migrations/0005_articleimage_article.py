# Generated by Django 5.0.4 on 2024-05-28 16:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogApp', '0004_articleimage_article_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='articleimage',
            name='article',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='blogApp.article'),
            preserve_default=False,
        ),
    ]