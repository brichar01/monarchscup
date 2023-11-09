from django.db import models
from enum import Enum

# Create your models here.
class RoundModel(models.Model):
    date = models.DateField(auto_now=True)
    round_num = models.IntegerField(default=0)


class TeamModel(models.Model):
    round = models.ForeignKey(RoundModel, models.CASCADE)


class GroupModel(models.Model):
    pass


class Matchup(Enum):
    MALE = True,
    FEMALE = False,
    NA = None

    def from_str(s: str):
        mu_list = list(filter(lambda x: x != None, [ matchup if s.startswith(matchup.name.lower()) else None for matchup in  list(Matchup)]))
        if len(mu_list) == 0:
            return Matchup.NA
        return mu_list[0]


class PlayerModel(models.Model):
    name = models.TextField(unique=True)
    matchup = models.BooleanField(default=True)
    experience = models.IntegerField()
    group = models.ForeignKey(GroupModel, models.CASCADE, null=True, default=None)
    attending = models.BooleanField(default=True)


class ParticipantModel(models.Model):
    team = models.ForeignKey(TeamModel, models.CASCADE)
    player = models.ForeignKey(PlayerModel, models.CASCADE)
    did_attend = models.BooleanField()


class ScoreModel(models.Model):
    points = models.IntegerField(default=0)
    spirit = models.IntegerField(default=0)
    mvp_1 = models.ForeignKey(PlayerModel, models.CASCADE, related_name="mvp1")
    mvp_2 = models.ForeignKey(PlayerModel, models.CASCADE, related_name="mvp2")

    
class GameModel(models.Model):
    round = models.ForeignKey(RoundModel, models.CASCADE)
    team_1 = models.ForeignKey(TeamModel, models.CASCADE, blank=True, related_name="team1")
    result_team_1 = models.ForeignKey(ScoreModel, models.CASCADE, related_name="team1_score")
    team_2 = models.ForeignKey(TeamModel, models.CASCADE, blank=True, related_name="team2")
    result_team_2 = models.ForeignKey(ScoreModel, models.CASCADE, related_name="team2_score")