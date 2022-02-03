from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('dragonlinguistics', '0005_alter_word_options'),
    ]

    operations = [
        migrations.DeleteModel('Sense'),
        migrations.DeleteModel('Word'),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lemma', models.CharField(max_length=50)),
                ('type', models.CharField(choices=[('r', 'Root'), ('br', 'Bound Root'), ('s', 'Stem'), ('pf', 'Prefix'), ('if', 'Infix'), ('sf', 'Suffix'), ('cf', 'Circumfix'), ('pc', 'Proclitic'), ('ec', 'Enclitic')], default='s', max_length=2)),
                ('notes', models.TextField(blank=True)),
                ('etymology', models.TextField(blank=True)),
                ('lang', models.ForeignKey(on_delete=models.deletion.CASCADE, to='dragonlinguistics.language', verbose_name='language')),
            ],
            options={
                'ordering': ['lemma', 'id'],
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
                ('word', models.ForeignKey(on_delete=models.deletion.CASCADE, to='dragonlinguistics.word')),
            ],
        ),
    ]
