from tournament.round_service import create_round, Grader, Player, Game, Team, PlayerComparer, show_round
from tournament.models import PlayerModel
from functools import reduce

def compare_teams_in_round(grader: Grader, game: Game) -> int:
    skill_diff = abs(grader.get_team_exp(game.team1) - grader.get_team_exp(game.team2))
    wins_diff = abs(grader.get_team_wins(game.team1) - grader.get_team_wins(game.team2))
    return wins_diff + skill_diff

def optimise_round(round: int):
    possible_rounds = [ create_round(round) for _ in range(0, 1) ]
    grader = Grader(PlayerComparer([ Player(player) for player in PlayerModel.objects.all() ]))
    best_round = sorted(possible_rounds, key=lambda games: reduce(lambda score, game: score + compare_teams_in_round(grader, game), games, 0))[0]
    show_round(best_round)
