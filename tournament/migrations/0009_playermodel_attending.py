# Generated by Django 4.1.7 on 2023-05-22 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0008_alter_gamemodel_result_team_1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='playermodel',
            name='attending',
            field=models.BooleanField(default=True),
        ),
    ]
