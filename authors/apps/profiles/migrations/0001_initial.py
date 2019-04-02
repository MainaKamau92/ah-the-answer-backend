# Generated by Django 2.1.7 on 2019-04-02 07:55

import cloudinary.models
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_bio', models.CharField(help_text='Write a brief description about yourself.', max_length=300)),
                ('name', models.CharField(help_text='Enter your first and last names.', max_length=50)),
                ('number_of_followers', models.IntegerField(default=0)),
                ('number_of_followings', models.IntegerField(default=0)),
                ('total_articles', models.IntegerField(default=0)),
                ('avatar', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]