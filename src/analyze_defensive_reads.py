import pandas as pd
import argparse
import sys

# CONSTANTS

RAW_DATA_DIR = "data/kaggle"
PROCESSED_DATA_DIR = "data/processed"

# FUNCTIONS

def get_game_ids_by_week(week):

    df_ = pd.read_csv(f"{RAW_DATA_DIR}/games.csv")
    df = df_[ df_[ "week" ] == week ]
    return df[ "gameId" ].unique()

def get_player_plays_from_game(game_id, player_id):

    df_ = df_pp[ ( df_pp[ "gameId" ] == game_id ) & \
                  ( df_pp[ "nflId" ] == player_id ) ]
    return df_[ "playId" ].unique()

def get_game_id_by_player_and_week( p_id, week ):

    df_ = pd.read_csv(f"{RAW_DATA_DIR}/player_play.csv")

    list_week_games = get_game_ids_by_week( week )
    df_plays_ = df_ [ ( df_[ "gameId" ].isin( list_week_games ) ) & \
                      ( df_[ "nflId" ] == p_id ) ]

    if (len(df_plays_) > 0):
        game_id = df_plays_[ "gameId" ].iloc[0]
    else:
        game_id = -1

    return game_id

def get_defensive_players_in_game_by_team( game_id, team ):

    l_defensive_players = []

    df_play = pd.read_csv(f"{RAW_DATA_DIR}/plays.csv")
    df_player_play = pd.read_csv(f"{RAW_DATA_DIR}/player_play.csv")

    #print(f"{game_id}, {team}")

    # find all plays where team was on defense
    df_defensive_plays = df_play[ ( df_play[ "gameId" ] == int(game_id) ) & \
                                  ( df_play[ "defensiveTeam" ] == team ) ]
    l_def_plays = df_defensive_plays[ "playId" ].unique()

    # get all players from team's defensive plays
    df_players = df_player_play[ ( df_player_play[ "gameId" ] == int(game_id) ) & \
                                 ( df_player_play[ "teamAbbr" ] == team ) & \
                                 ( df_player_play[ "playId" ].isin(l_def_plays) ) ]
    l_defensive_players = df_players[ "nflId" ].unique()

    return l_defensive_players

def get_game_ids_by_player( p_id ):

    week_start = 1
    week_end = 6

    list_game_ids = []

    for w in range(week_start, week_end + 1):
        game = get_game_id_by_player_and_week( p_id, w )
        if game > 0:
            list_game_ids.append( game )

    return list_game_ids

# parse arguments for game_id and player_id
parser = argparse.ArgumentParser( description='Analyze how well defensive players \
                                               can read an offense' )
parser.add_argument( '-g', '--game',   help='Specify game_id (leave blank to analyze \
                                             all games in weeks 1 - 6)' )
parser.add_argument( '-p', '--player', help='Specify player_id (leave blank to \
                                             analyze all defensive players per game)' )
parser.add_argument( '-t', '--team',   help='If no player_id, get all defensive players' \
                                            'from team' )
args = vars( parser.parse_args() )

s_team = args["team"]
s_player = args["player"]
s_game = args["game"]

# if no player or game is specified, then set the boolean to pull all data
if s_player:
    player_ids = [ int(s_player) ]
    all_players = False
else:
    player_ids = get_defensive_players_in_game_by_team(s_game, s_team)
    all_players = True

if s_game:
    game_ids = [ int(s_game) ]
    all_games = False
else:
    # if the game isn't specified, we assume that there's just one player
    game_ids = get_game_ids_by_player( player_ids[0] )
    all_games = True

pp_filename = "player_play.csv"
ps_filename = "players.csv"
p_filename  = "plays.csv"
pt_filename = "plays_and_targets.csv"

# load data from csv
df_pp = pd.read_csv(f"{RAW_DATA_DIR}/{pp_filename}")
df_ps = pd.read_csv(f"{RAW_DATA_DIR}/{ps_filename}")
df_p  = pd.read_csv(f"{RAW_DATA_DIR}/{p_filename}")
df_pt = pd.read_csv(f"{PROCESSED_DATA_DIR}/{pt_filename}")

# merge the play target dataframe with the player play dataframe
# AND the play dataframe
df_mp = df_pp.merge( df_pt, on=[ 'gameId', 'playId' ] )
df_mt = df_p.merge( df_pt, on=[ 'gameId', 'playId' ] )

print(f"Found games: {game_ids}")

l_players = []

for g in game_ids:

    # make a list of the defensive plays that this team ran in the game
    df_team_ = df_mt[ ( df_mt[ "defensiveTeam" ] == s_team ) & \
                      ( df_mt[ "gameId" ] == g ) ]
    list_all_def_plays = df_team_[ "playId" ].unique()

    # how many team plays were offense success vs. defense success?
    team_defense_target_sum = df_team_[ 'defenseTarget' ].sum()
    team_offense_target_sum = df_team_[ 'offenseTarget' ].sum()
    team_target_score = -df_team_['targetDiff' ].sum()

    for p in player_ids:

        # get frame for all of the plays this player participated in
        df_part_ = df_mp[ ( df_mp[ "gameId" ] == g ) & \
                          ( df_mp[ "nflId" ] == p ) ]
        if df_part_.empty:
            print(f"WARN: Player did not participate in game {g}")
            continue
        #else:
            #print(len(df_part_))

        list_played_plays = df_part_[ "playId" ].unique()
        if not s_team:
            s_team = df_part_.iloc[0]["teamAbbr"]

        # how many plays were offensive success vs. defensive success? (assign a score)
        defense_target_sum = df_part_[ 'defenseTarget' ].sum()
        offense_target_sum = df_part_[ 'offenseTarget' ].sum()
        target_score = -df_part_['targetDiff' ].sum()

        # pull player data based on player_id
        row_p = df_ps[ df_ps[ "nflId" ] == int(p) ]
        player_name = row_p['displayName'].values[0]
        player_pos = row_p['position'].values[0]

        #print(f"part: {len(list_played_plays)} all: {len(list_all_def_plays)}")
        #print(f"played: {list_played_plays}")
        #print(f"all:    {list_all_def_plays}")

        if set(list_played_plays).issubset(list_all_def_plays):

            participated_play_count = len(list_played_plays)
            total_def_play_count = len(list_all_def_plays)
            defense_score_per_play = defense_target_sum / participated_play_count
            team_defense_score_per_play = team_defense_target_sum / total_def_play_count

            diff_score_per_play = defense_score_per_play - team_defense_score_per_play
            defense_score_over_team = diff_score_per_play * participated_play_count

            #if all_games:
            #    print(f"Found games: {game_ids}")

            l_players.append( [ g, p, player_name, player_pos, s_team, participated_play_count, total_def_play_count,
                                defense_target_sum, offense_target_sum, target_score, defense_score_per_play,
                                team_defense_target_sum, team_offense_target_sum, team_target_score,
                                team_defense_score_per_play, diff_score_per_play, defense_score_over_team ] )

        else:
            print("No defensive plays found")

columns = [ 'gameId', 'nflId', 'displayName', 'position', 'teamAbbr', 'playCount', 'teamPlayCount', 'successfulDefensePlays',
            'successfulOffensePlays', 'defenseScore', 'defenseScorePerPlay', 'successfulTeamDefensePlays',
            'successfulTeamOffensePlays', 'teamDefenseScore', 'teamDefenseScorePerPlay', 'diffScorePerPlay',
            'defenseScoreOverTeam' ]
df_out = pd.DataFrame( l_players, columns=columns )
print(df_out)
#print(df_out.to_string(index=False))
