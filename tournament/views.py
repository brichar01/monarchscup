from django.shortcuts import render
from django.http.request import HttpRequest
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
import json
from tournament.models import RoundModel, Matchup, PlayerModel
from tournament.src.round_service import get_round_summary, get_new_round, Player
from tournament.src.score_service import get_player_wins, get_player_spirit, count_player_mvp_votes
from tournament.src.add_results import add_round, TeamWithScore

# Create your views here.
    
def get_round(request: HttpRequest, round: int):
    if round < 1:
        return HttpResponseBadRequest(f'Bad round: {round}')
    rounds = RoundModel.objects.filter(round_num=round)
    if len(rounds) == 0: 
        return HttpResponseNotFound()
    elif len(rounds) > 1:
        print(f'{len(rounds)} rounds found')
    return JsonResponse({'rounds': [{'round_id': r.id, 'games': get_round_summary(r).games} for r in rounds]})

def get_player_scores(request: HttpRequest, matchup: str):
    mu = Matchup.from_str(matchup)
    return JsonResponse({'players': get_player_wins(mu)})

def get_player_spirits(request: HttpRequest):
    return JsonResponse({'players': get_player_spirit()})

def get_player_mvp_votes(request: HttpRequest):
    return JsonResponse({'players': count_player_mvp_votes()})

def generate_teams(request: HttpRequest):
    return JsonResponse({
        'games': get_new_round()
    })

def generate_team_constrained(request: HttpRequest):
    data = json.loads(request.body.decode())
    games = list([( [ Player(PlayerModel.objects.get(name=player)) for player in game['team1'] ], 
                    [ Player(PlayerModel.objects.get(name=player)) for player in game['team2'] ] )
        for game in data['games'] ])
    return JsonResponse({
        'games': get_new_round(games)
    })

def post_results(request: HttpRequest):
    data = json.loads(request.body.decode())
    round_num = data['round']
    if RoundModel.objects.filter(round_num=round_num).exists():
        return HttpResponseBadRequest("already posted this round")
    games = list([( TeamWithScore(game['team1']['players'],
                                    game['team1']['score'],
                                    game['team1']['spirit'],
                                    game['team1']['mvps']),
                    TeamWithScore(game['team2']['players'],
                                    game['team2']['score'],
                                    game['team2']['spirit'],
                                    game['team2']['mvps']) )
        for game in data['games'] ])
    r = add_round(round_num, games)
    return JsonResponse({'created_round': get_round_summary(r).games})