# Generated by Django 3.2.9 on 2022-02-02 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dragonlinguistics', '0002_auto_20220202_1058'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reference',
            options={'ordering': ['author', 'year', 'id']},
        ),
    ]