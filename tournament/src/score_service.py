from django.db.models import Q
from tournament.models import PlayerModel, ParticipantModel, GameModel, TeamModel, Matchup

def team_did_win(game: GameModel, team: TeamModel):
    if game.team_1 == team and game.result_team_1.points > game.result_team_2.points:
        return True
    if game.team_2 == team and game.result_team_2.points > game.result_team_1.points:
        return True
    return False

def team_points_diff(game: GameModel, team: TeamModel):
    if game.team_1 == team:
        return game.result_team_1.points - game.result_team_2.points
    if game.team_2 == team:
        return game.result_team_2.points - game.result_team_1.points
    return 0

def get_spirit_score_for_team(game: GameModel, team: TeamModel):
    if game.team_1 == team:
        return game.result_team_1.spirit
    if game.team_2 == team:
        return game.result_team_2.spirit
    return 0

def get_player_wins(matchup: Matchup):
    players = PlayerModel.objects.all()
    if matchup != Matchup.NA:
        players = players.filter(matchup=matchup.value[0])
    player_attendance = [ { "player": player, "attendance": ParticipantModel.objects.filter(player=player).filter(did_attend=True) } for player in players ]
    player_wins: list[dict] = []
    for p in player_attendance:
        games_player_played_in = [ { 'team': participant.team, 'game': GameModel.objects.filter(Q(team_1=participant.team)|Q(team_2=participant.team)).first()} for participant in p['attendance'] ]
        record = [ team_did_win(games_played_in['game'], games_played_in['team']) for games_played_in in games_player_played_in ]
        points_diff_record = [ team_points_diff(games_played_in['game'], games_played_in['team']) for games_played_in in games_player_played_in ]
        wins = sum([1 if r else 0 for r in record ])
        points_diff = sum([1 if r else 0 for r in points_diff_record ])
        player_wins.append({ "player": p['player'].name, "wins": wins, "points_diff": points_diff })
    return sorted(sorted(player_wins, key=lambda p: -p['points_diff']), key=lambda p: -p['wins'])

def get_player_spirit():
    players = PlayerModel.objects.all()
    player_attendance = [ { "player": player, "attendance": ParticipantModel.objects.filter(player=player).filter(did_attend=True) } for player in players ]
    player_wins: list[dict] = []
    for p in player_attendance:
        games_player_played_in = [ { 'team': participant.team, 'game': GameModel.objects.filter(Q(team_1=participant.team)|Q(team_2=participant.team)).first()} for participant in p['attendance'] ]
        spirit_scores = [ get_spirit_score_for_team(games_played_in['game'], games_played_in['team']) for games_played_in in games_player_played_in ]
        spirit_total = sum(spirit_scores)
        player_wins.append({ "player": p['player'].name, "total_spirit": spirit_total })
    return sorted(player_wins, key=lambda p: -p['total_spirit'])

def count_player_mvp_votes():
    return sorted([ {'player': player.name, 
                     'mvp_votes': GameModel.objects.filter(Q(result_team_1__mvp_1=player)|
                                                           Q(result_team_1__mvp_2=player)|
                                                           Q(result_team_2__mvp_1=player)|
                                                           Q(result_team_2__mvp_2=player)).count()} for player in PlayerModel.objects.all() ],
        key=lambda p: -p['mvp_votes'])
        