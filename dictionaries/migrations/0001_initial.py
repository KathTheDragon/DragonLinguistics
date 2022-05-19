# Generated by Django 4.0.4 on 2022-05-17 11:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('languages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dictionary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classes', models.TextField(blank=True, verbose_name='lexical classes')),
                ('order', models.TextField(blank=True, verbose_name='alphabetical order')),
                ('language', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='languages.language')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lemma', models.CharField(max_length=50)),
                ('type', models.CharField(choices=[('r', 'Root'), ('s', 'Stem'), ('pf', 'Prefix'), ('if', 'Infix'), ('sf', 'Suffix'), ('cf', 'Circumfix'), ('pc', 'Proclitic'), ('ec', 'Enclitic')], default='s', max_length=2)),
                ('isunattested', models.BooleanField(default=False)),
                ('etymology', models.TextField(blank=True)),
                ('descendents', models.TextField(blank=True)),
                ('references', models.TextField(blank=True)),
                ('dictionary', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='words', related_query_name='word', to='dictionaries.dictionary')),
            ],
            options={
                'ordering': ['lemma', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lexclass', models.CharField(max_length=20, verbose_name='class')),
                ('forms', models.TextField(blank=True)),
                ('definition', models.TextField()),
                ('notes', models.TextField(blank=True)),
                ('derivatives', models.TextField(blank=True)),
                ('word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', related_query_name='variant', to='dictionaries.word')),
            ],
        ),
    ]
