# Generated by Django 4.1.7 on 2023-05-15 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='playermodel',
            name='matchup',
            field=models.BooleanField(null=True),
        ),
    ]
