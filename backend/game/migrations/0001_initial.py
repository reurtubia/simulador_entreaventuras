# Generated by Django 4.0.6 on 2022-10-03 02:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=30)),
                ('player', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'unique_together': {('name', 'player')},
            },
        ),
        migrations.CreateModel(
            name='CharacterProgression',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('level', models.IntegerField()),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.character')),
            ],
            options={
                'unique_together': {('character', 'level')},
            },
        ),
        migrations.CreateModel(
            name='DnDClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=10, unique=True)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DnDSubclass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=30)),
                ('dndclass', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.dndclass')),
            ],
            options={
                'unique_together': {('name', 'dndclass')},
            },
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Multiclass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('level', models.IntegerField()),
                ('characterprogression', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.characterprogression')),
                ('dndsubclass', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.dndsubclass')),
            ],
            options={
                'unique_together': {('characterprogression', 'level')},
            },
        ),
    ]
