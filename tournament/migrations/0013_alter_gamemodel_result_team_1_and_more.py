# Generated by Django 4.1.7 on 2023-06-12 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0012_rename_points_team_1_scoremodel_points_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamemodel',
            name='result_team_1',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='team1_score', to='tournament.scoremodel'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='gamemodel',
            name='result_team_2',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='team2_score', to='tournament.scoremodel'),
            preserve_default=False,
        ),
    ]
