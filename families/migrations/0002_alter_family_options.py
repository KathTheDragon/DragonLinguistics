# Generated by Django 4.0.4 on 2022-08-06 21:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='family',
            options={'ordering': ['name']},
        ),
    ]
