# Generated by Django 3.0.4 on 2020-03-24 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_song_thumbnail_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song',
            name='thumbnail_url',
        ),
    ]
