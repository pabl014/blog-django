# Generated by Django 5.0.4 on 2024-06-04 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogApp', '0006_alter_articleimage_article'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='content',
            field=models.CharField(max_length=2000),
        ),
    ]
