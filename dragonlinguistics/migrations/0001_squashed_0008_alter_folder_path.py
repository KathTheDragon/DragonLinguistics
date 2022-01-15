# Generated by Django 3.2.9 on 2022-01-15 17:11

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='language name')),
                ('code', models.CharField(max_length=5, unique=True, verbose_name='language code')),
                ('blurb', models.TextField(default='')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lemma', models.CharField(max_length=50)),
                ('homonym', models.IntegerField(default=0)),
                ('type', models.CharField(choices=[('r', 'Root'), ('br', 'Bound Root'), ('s', 'Stem'), ('pf', 'Prefix'), ('if', 'Infix'), ('sf', 'Suffix'), ('cf', 'Circumfix'), ('pc', 'Proclitic'), ('ec', 'Enclitic')], default='s', max_length=2)),
                ('notes', models.TextField(blank=True)),
                ('etymology', models.TextField(blank=True)),
                ('lang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dragonlinguistics.language', verbose_name='language')),
            ],
            options={
                'ordering': ['lemma', 'homonym'],
            },
        ),
        migrations.CreateModel(
            name='Sense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gloss', models.CharField(max_length=20)),
                ('defin', models.TextField(blank=True, verbose_name='definition')),
                ('pos', models.CharField(choices=[('aff', 'Affix'), ('adj', 'Adjective'), ('adp', 'Adposition'), ('adv', 'Adverb'), ('conj', 'Conjunction'), ('det', 'Determiner'), ('intj', 'Interjection'), ('n', 'Noun'), ('num', 'Numeral'), ('part', 'Particle'), ('pron', 'Pronoun'), ('pn', 'Proper Noun'), ('unk', 'Unknown'), ('v', 'Verb')], default='unk', max_length=4, verbose_name='part of speech')),
                ('grammclass', models.CharField(blank=True, max_length=20, verbose_name='class')),
                ('notes', models.TextField(blank=True)),
                ('word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dragonlinguistics.word')),
            ],
        ),
        migrations.AddConstraint(
            model_name='word',
            constraint=models.UniqueConstraint(fields=('lang', 'lemma', 'homonym'), name='unique-homonym'),
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('title', models.CharField(max_length=255)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('content', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('folder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dragonlinguistics.folder')),
                ('tags', models.TextField(blank=True)),
            ],
        ),
    ]