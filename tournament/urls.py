from django.urls import path

from tournament.views import get_round, get_player_scores, get_player_spirits, get_player_mvp_votes, generate_teams, post_results, generate_team_constrained

urlpatterns = [
    path('round/<int:round>', get_round),
    path('player-scores/<str:matchup>', get_player_scores),
    path('player-spirits', get_player_spirits),
    path('player-mvps', get_player_mvp_votes),
    path('round/new', generate_teams),
    path('round/seeded', generate_team_constrained),
    path("round/report", post_results)
]
