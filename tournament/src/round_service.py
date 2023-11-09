from typing import List, Tuple
from tournament.models import RoundModel, GameModel, ParticipantModel, PlayerModel
from tournament.round_service import create_round, Grader, Player, Game, PlayerComparer
from functools import reduce


class RoundSummary:
    def __init__(self) -> None:
        self.games = []

    def add_team(
            self,
            players: List[str],
            score: int,
            spirit: int,
            mvps: List[str]):
        self.games.append({
            'players': players,
            'score': score,
            'spirit': spirit,
            'mvps': mvps
        })


def compare_teams_in_round(grader: Grader, game: Game) -> int:
    skill_diff = abs(grader.get_team_exp(game.team1) - grader.get_team_exp(game.team2))
    wins_diff = abs(grader.get_team_wins(game.team1) - grader.get_team_wins(game.team2))
    return wins_diff + skill_diff


def get_round_summary(round: RoundModel) -> RoundSummary:
    games = list(GameModel.objects.filter(round=round))
    round_summary = RoundSummary()
    for game in games:
        team1_players = [ p.player.name for p in ParticipantModel.objects.filter(team=game.team_1) ]
        team2_players = [ p.player.name for p in ParticipantModel.objects.filter(team=game.team_2) ]
        round_summary.add_team(team1_players, game.result_team_1.points, game.result_team_1.spirit, [ p.name for p in [ game.result_team_1.mvp_1, game.result_team_1.mvp_2 ] ])
        round_summary.add_team(team2_players, game.result_team_2.points, game.result_team_2.spirit, [ p.name for p in [ game.result_team_2.mvp_1, game.result_team_2.mvp_2 ] ])
    return round_summary


def get_new_round(starting_teams: List[Tuple[List[Player], List[Player]]] = None):

    possible_rounds = [ create_round(starting_teams=starting_teams) for _ in range(0, 500) ]
    grader = Grader(PlayerComparer([ Player(player) for player in PlayerModel.objects.all() ]))
    best_round = sorted(possible_rounds, key=lambda games: reduce(lambda score, game: score + compare_teams_in_round(grader, game), games, 0))[0]
    return [ 
        { 
            'team1': [ player.ref.name for player in game.team1.players ], 
            'team2': [ player.ref.name for player in game.team2.players ]
        } for game in best_round 
    ]