# Generated by Django 4.2.4 on 2023-10-28 15:49

import Users.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('mobile', models.BigIntegerField(unique=True, validators=[Users.models.mobile_validator])),
                ('room', models.CharField(max_length=8)),
                ('state', models.CharField(max_length=25)),
                ('profile_photo', models.ImageField(default='Users/Profile/profile_photo/default.jpg', upload_to=Users.models.upload_path, validators=[Users.models.validate_image_size])),
                ('isRep', models.BooleanField(default=False)),
                ('isSecy', models.BooleanField(default=False)),
                ('isVerified', models.BooleanField(default=False)),
                ('otp', models.CharField(blank=True, max_length=6, null=True)),
                ('points', models.IntegerField(default=0)),
                ('registered_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=150)),
                ('message', models.TextField(max_length=1000)),
                ('isSolved', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
