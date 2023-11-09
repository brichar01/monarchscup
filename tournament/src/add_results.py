from tournament.models import GameModel, GroupModel, ParticipantModel, PlayerModel, RoundModel, ScoreModel, TeamModel
from django.db.models import Q
from typing import List


class TeamWithScore:
    def __init__(self, players: List[str], score: int, spirit: int, mvps: List[str]):
        self.players = players
        self.score = score
        self.spirit = spirit
        self.mvps = mvps


def get_players_from_name(players: str):
    return [ PlayerModel.objects.filter(name=player_name)[0] if PlayerModel.objects.filter(name=player_name).exists() else print(f"{player_name} does not exist") for player_name in [ player.strip('\' ') for player in players ] ]


def create_team(round, players):
    team = TeamModel(round=round)
    team.save()
    for player in players:
        ParticipantModel(team=team, player=player, did_attend=True).save()
    return team


def create_game(round, t1: TeamWithScore, t2: TeamWithScore):
    team1 = create_team(round, get_players_from_name(t1.players))
    team2 = create_team(round, get_players_from_name(t2.players))
    t1_mvp_players = get_players_from_name(t1.mvps);
    t1_result = ScoreModel(points = t1.score, spirit = t1.spirit, mvp_1 = t1_mvp_players[0], mvp_2 = t1_mvp_players[1])
    t1_result.save()
    t2_mvp_players = get_players_from_name(t2.mvps);
    t2_result = ScoreModel(points = t2.score, spirit = t2.spirit, mvp_1 = t2_mvp_players[0], mvp_2 = t2_mvp_players[1])
    t2_result.save()
    game = GameModel(round=round, team_1=team1, result_team_1=t1_result, team_2=team2, result_team_2=t2_result)
    game.save()


def add_round(round_num, games: List[tuple[TeamWithScore, TeamWithScore]]):
    round = RoundModel(round_num=round_num)
    round.save()
    
    [ create_game(round, teams[0], teams[1]) for teams in games ]

    return round


def team_did_win(game: GameModel, team: TeamModel):
    if game.team_1 == team and game.result_team_1.points > game.result_team_2.points:
        return True
    if game.team_2 == team and game.result_team_2.points > game.result_team_1.points:
        return True
    return False

def get_player_wins():
    players = PlayerModel.objects.all()
    player_attendance = [ { "player": player, "attendance": ParticipantModel.objects.filter(player=player) } for player in players ]
    player_wins = []
    for p in player_attendance:
        games_player_played_in = [ { 'team': participant.team, 'game': GameModel.objects.filter(Q(team_1=participant.team)|Q(team_2=participant.team)).first()} for participant in p['attendance'] ]
        record = [ team_did_win(games_played_in['game'], games_played_in['team']) for games_played_in in games_player_played_in ]
        wins = sum([1 if r else 0 for r in record ])
        player_wins.append({ "player": p['player'].name, "wins": wins })
    return player_wins