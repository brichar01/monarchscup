# Generated by Django 4.1.7 on 2023-06-12 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0011_remove_scoremodel_points_team_2'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scoremodel',
            old_name='points_team_1',
            new_name='points',
        ),
        migrations.AddField(
            model_name='scoremodel',
            name='spirit',
            field=models.IntegerField(default=0),
        ),
    ]
