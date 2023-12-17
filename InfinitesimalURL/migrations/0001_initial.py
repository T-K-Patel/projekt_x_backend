# Generated by Django 4.2.7 on 2023-11-21 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ShortURL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('url', models.URLField()),
                ('last_visited', models.DateTimeField(blank=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]