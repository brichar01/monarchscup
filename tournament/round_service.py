import random
from functools import reduce
from typing import List, Tuple
from django.db.models import Q
from tournament.models import ParticipantModel, TeamModel, PlayerModel, RoundModel, GroupModel, GameModel


def team_did_win(game: GameModel, team: TeamModel):
    if game.team_1 == team and game.result_team_1.points > game.result_team_2.points:
        return True
    if game.team_2 == team and game.result_team_2.points > game.result_team_1.points:
        return True
    return False

class Player:
    def __init__(self, model: PlayerModel) -> None:
        self._model = model
        self.participation = list(ParticipantModel.objects.filter(Q(player=self._model) & Q(did_attend=True)))
    
    def get_score(self):
        games_player_played_in = [ { 'team': participant.team, 'game': GameModel.objects.filter(Q(team_1=participant.team)|Q(team_2=participant.team)).first()} for participant in self.participation ]
        record = [ team_did_win(games_played_in['game'], games_played_in['team']) for games_played_in in games_player_played_in ]
        return sum([1 if r else 0 for r in record ])
    
    @property
    def ref(self):
        return self._model


class Team:
    def __init__(self, round: RoundModel):
        self.round = round
        self.players: list[Player] = []
    
    def save(self): 
        self._model.save()

    def create_participants(self):
        [ participant.save() for participant in [ ParticipantModel(team=self.ref, player=player._model, did_attend=True) for player in self.players ] ]

    def set_round(self, round):
        self._model.round = round
        self._model.save()

    def get_round(self):
        return self._model.round
    
    @property
    def ref(self):
        return self._model
    

class Game:
    def __init__(self, round, new_round = False):
        self.team1 = Team(round=round)
        self.team2 = Team(round=round)

    def add_players(self, players: List[Player], team_num: int):
        if (team_num == 0):
            [ self.team1.players.append(player) for player in players ]
        else:
            [ self.team2.players.append(player) for player in players ]
    

def flatmap(list_of_lists): 
    return reduce(lambda list1, list2: list1+list2 if list2 != None else list1, list_of_lists)


def get_players_for_game(players_by_exp: List[List[Player]]):
    while any([len(player_exp) > 0 for player_exp in players_by_exp]):
        # select a random experience level
        remaining_players: List[List[Player]] = list(filter(lambda players_in_exp: len(players_in_exp) > 0, players_by_exp))
        exp_level: List[Player] = random.sample(remaining_players, 1)[0]
        # add it to a list of players for team 1
        random.shuffle(exp_level)
        players_to_add_t1: List[Player] = [ exp_level.pop() ]
        # get their group members from all skill levels and add to list
        if (players_to_add_t1[0].ref.group != None):
            for exp in range(0, len(players_by_exp)):
                players_in_exp = list(filter(lambda player: player.ref.group == players_to_add_t1[0].ref.group, players_by_exp[exp]))
                [ players_by_exp[exp].remove(player) for player in players_in_exp ]
                players_to_add_t1.extend(players_in_exp)
        # try to do the same for team 2
        if len(exp_level) > 0:
            players_to_add_t2: List[Player] = [ exp_level.pop() ]
            if (players_to_add_t2[0].ref.group != None):
                for exp in range(0, len(players_by_exp)):
                    players_in_exp = list(filter(lambda player: player.ref.group == players_to_add_t2[0].ref.group, players_by_exp[exp]))
                    [ players_by_exp[exp].remove(player) for player in players_in_exp ]
                    players_to_add_t2.extend(players_in_exp)
            yield players_to_add_t1, players_to_add_t2
        else:
            yield players_to_add_t1, None
    yield None, None


def create_round(round: int = 0, starting_teams: List[Tuple[List[Player], List[Player]]] = None):
    round_inst = RoundModel(round_num=round)
    # round_inst.save()
    decided_players = [ player.ref.id for player in flatmap(flatmap(starting_teams)) ]
    print(decided_players)
    players = list(filter(lambda p: p.ref.id not  in decided_players, list([Player(player) for player in PlayerModel.objects.filter(attending=True)])))
    print([player.ref.id for player in players])
    fm_by_exp = list([ [] for i in range(0, 4) ])
    m_by_exp = list([ [] for i in range(0, 4) ])
    [ m_by_exp[player.ref.experience].append(player) if player.ref.matchup == True else fm_by_exp[player.ref.experience].append(player) for player in players ]
    num_games = int((len(players) + len(decided_players)) / 16)
    games = [ Game(round=round_inst) for i in range(0, num_games) ]
    if starting_teams:
        for i in range(0, len(starting_teams)):
            games[i].add_players(starting_teams[i][0], 0)
            games[i].add_players(starting_teams[i][1], 1)

    
    # add all girls to the first game
    player_generator = get_players_for_game(fm_by_exp)
    players_to_add_t1 = []
    players_to_add_t2 = []
    while not (players_to_add_t1 == None and players_to_add_t2 == None):
        players_to_add_t1, players_to_add_t2 = next(player_generator)
        team_add_order = sorted(range(2), key=(lambda i: len(games[0].team1.players) if i == 0 else len(games[0].team2.players)))
        if players_to_add_t1 != None:
            games[0].add_players(players_to_add_t1, team_add_order[0])
        if players_to_add_t2 != None:
            games[0].add_players(players_to_add_t2, team_add_order[1])

    # add players from any mixed groups added
    mixed_groups_t1 = [ player.ref.group for player in filter(lambda player: (player.ref.group != None), games[0].team1.players) ]
    mixed_players_t1 = []
    for exp in range(0, len(m_by_exp)):
        players_in_exp = list(filter(lambda player: player.ref.group in mixed_groups_t1, m_by_exp[exp]))
        [ m_by_exp[exp].remove(player) for player in players_in_exp ]
        mixed_players_t1.extend(players_in_exp)
    games[0].add_players(mixed_players_t1, 0)

    mixed_groups_t2 = [ player.ref.group for player in filter(lambda player: (player.ref.group != None), games[0].team2.players) ]
    mixed_players_t2 = []
    for exp in range(0, len(m_by_exp)):
        players_in_exp = list(filter(lambda player: player.ref.group in mixed_groups_t2, m_by_exp[exp]))
        [ m_by_exp[exp].remove(player) for player in players_in_exp ]
        mixed_players_t2.extend(players_in_exp)
    games[0].add_players(mixed_players_t2, 1)

    player_generator = get_players_for_game(m_by_exp)
    players_to_add_t1 = []
    players_to_add_t2 = []
    while not (players_to_add_t1 == None and players_to_add_t2 == None):
        smallest_game_ind = reduce(lambda smallest_game_i, game_i: game_i if len(games[game_i].team1.players) < len(games[smallest_game_i].team1.players) else smallest_game_i, range(0, num_games))
        team_add_order = sorted(range(2), key=(lambda i: len(games[smallest_game_ind].team1.players) if i == 0 else len(games[smallest_game_ind].team2.players)))
        players_to_add_t1, players_to_add_t2 = next(player_generator)
        players_add_order = [players_to_add_t1, players_to_add_t2]
        if (players_to_add_t1 != None and players_to_add_t2 != None):
          players_add_order= sorted(players_add_order, key=(lambda players: len(players)), reverse=True)
        if players_to_add_t1 != None:
            games[smallest_game_ind].add_players(players_add_order[0], team_add_order[0])
        if players_to_add_t2 != None: 
            games[smallest_game_ind].add_players(players_add_order[1], team_add_order[1])
    return games


def show_round(games: List[Game]):
    grader = Grader(PlayerComparer([Player(player) for player in PlayerModel.objects.all()]))
    print([player.ref.name for player in games[0].team1.players])
    print(f'{len(games[0].team1.players)}, {grader.get_team_wins(games[0].team1)}, {grader.get_team_exp(games[0].team1)}')
    print([player.ref.name for player in games[0].team2.players])
    print(f'{len(games[0].team2.players)}, {grader.get_team_wins(games[0].team2)}, {grader.get_team_exp(games[0].team2)}')
    print([player.ref.name for player in games[1].team1.players])
    print(f'{len(games[1].team1.players)}, {grader.get_team_wins(games[1].team1)}, {grader.get_team_exp(games[1].team1)}')
    print([player.ref.name for player in games[1].team2.players])
    print(f'{len(games[1].team2.players)}, {grader.get_team_wins(games[1].team2)}, {grader.get_team_exp(games[1].team2)}')


class PlayerComparer:
    class PlayerStat:
        def __init__(self, player: Player, wins: int):
            self.player = player
            self.wins = wins

    player_stats: List[PlayerStat] = []

    def __init__(self, players: list[Player]) -> None:
        self.player_stats = list([ self.PlayerStat(player, player.get_score()) for player in players])

    def get_player_score(self, player: Player):
        for p in self.player_stats:
            if p.player.ref.name == player.ref.name:
                return p.wins
        return 0


class Grader:
    exp_factor = 0.1
    win_factor = 10.0
    player_factor = 1.0

    def __init__(self, player_comparer: PlayerComparer) -> None:
        self.player_comparer = player_comparer

    def get_team_exp(self, team: Team):
        return sum([ player.ref.experience for player in team.players ]) * self.exp_factor
    
    def get_team_wins(self, team: Team):
        return sum([ self.player_comparer.get_player_score(player) for player in team.players ]) * self.win_factor
    
    def get_team_size_score(self, team: Team):
        return len(team.players) * self.player_factor


def create_group(players):
    player_insts = [ PlayerModel.objects.get(name__contains=player) for player in players ]
    _create_group(player_insts)


def _create_group(players: List[PlayerModel]):
    group = GroupModel()
    group.save()
    for player in players:
        player.group = group    
        player.save()


def create_player(name, experience, matchup):
    player = PlayerModel(name=name, matchup=matchup, experience=experience)
    player.save()
