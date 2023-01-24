# Generated by Django 4.0.4 on 2022-11-25 18:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dictionaries', '0002_rename_forms_variant_extra_forms_variant_form_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variant',
            name='derivatives',
        ),
        migrations.RemoveField(
            model_name='word',
            name='descendents',
        ),
        migrations.RemoveField(
            model_name='word',
            name='etymology',
        ),
        migrations.RemoveField(
            model_name='word',
            name='type',
        ),
        migrations.AddField(
            model_name='dictionary',
            name='derivations',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='variant',
            name='type',
            field=models.CharField(choices=[('r', 'Root'), ('s', 'Stem'), ('w', 'Word'), ('pf', 'Prefix'), ('if', 'Infix'), ('sf', 'Suffix'), ('cf', 'Circumfix'), ('pc', 'Proclitic'), ('ec', 'Enclitic')], default='s', max_length=2),
        ),
        migrations.CreateModel(
            name='Etymology',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(max_length=7)),
                ('notes', models.TextField(blank=True)),
                ('order', models.TextField()),
                ('components', models.ManyToManyField(related_name='derivatives', related_query_name='derivative', to='dictionaries.variant')),
                ('word', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dictionaries.word')),
            ],
        ),
    ]