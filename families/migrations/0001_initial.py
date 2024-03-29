# Generated by Django 4.0.4 on 2022-08-06 15:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('languages', '0002_language_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('type', models.CharField(choices=[('natlang', 'Natlang'), ('conlang', 'Conlang'), ('other', 'Other')], default='other', max_length=7)),
                ('blurb', models.TextField(default='')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Clade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clades', related_query_name='clade', to='families.family')),
                ('language', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='languages.language')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', related_query_name='child', to='families.clade')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
