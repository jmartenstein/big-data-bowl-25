import pandas as pd
import argparse
import sys

# CONSTANTS

DATA_DIR = "data/kaggle"

# FUNCTIONS

def get_game_ids_by_week(week):
    df_ = pd.read_csv(f"{DATA_DIR}/games.csv")
    df = df_[ df_[ "week" ] == week ]
    return df[ "gameId" ].unique()

def get_player_plays_from_game(game_id, player_id):
    df_part_ = df_pp[ ( df_pp[ "gameId" ] == game_id ) & \
                      ( df_pp[ "nflId" ] == player_id ) ]
    return df_part_[ "playId" ].unique()

def get_game_id_by_player_and_week( p_id, week ):

    df_ = pd.read_csv(f"{DATA_DIR}/player_play.csv")

    list_week_games = get_game_ids_by_week( week )
    df_plays_ = df_ [ ( df_[ "gameId" ].isin( list_week_games ) ) & \
                      ( df_[ "nflId" ] == p_id ) ]

    if (len(df_plays_) > 0):
        game_id = df_plays_[ "gameId" ].iloc[0]
    else:
        game_id = -1

    return game_id

def get_game_ids_by_player( p_id ):

    week_start = 1
    week_end = 6

    list_game_ids = []

    for w in range(week_start, week_end + 1):
        game = get_game_id_by_player_and_week( p_id, w )
        list_game_ids.append( game )

    return list_game_ids

# parse arguments for game_id and player_id
parser = argparse.ArgumentParser( description='Analyze how well defensive players \
                                               can read an offense' )
parser.add_argument( '-g', '--game',     help='Specify game_id (leave blank to analyze \
                                               all games in weeks 1 - 6)' )
parser.add_argument( '-p', '--player',   help='Specify player_id (leave blank to \
                                               analyze all defensive players per game' )
args = vars( parser.parse_args() )

# if no player or game is specified, then set the boolean to pull all data
s_player = args["player"]
if s_player:
    player_id = int(s_player)
    all_players = False
else:
    all_players = True

s_game = args["game"]
if s_game:
    game_ids = [ int(s_game) ]
    all_games = False
else:
    game_ids = get_game_ids_by_player( player_id )
    all_games = True

pp_filename = "player_play.csv"
ps_filename = "players.csv"
p_filename  = "plays.csv"

# load data from csv
df_pp = pd.read_csv(f"{DATA_DIR}/{pp_filename}")
df_ps = pd.read_csv(f"{DATA_DIR}/{ps_filename}")
df_p  = pd.read_csv(f"{DATA_DIR}/{p_filename}")

# get frame for all of the plays this player  participated in?
df_part_ = df_pp[ ( df_pp[ "gameId" ].isin( game_ids ) ) & \
                  ( df_pp[ "nflId" ] == player_id ) ]
s_team = df_part_.iloc[0]["teamAbbr"]
list_played_plays = df_part_[ "playId" ].unique()

# make a list of the defensive plays that this team ran in the game
df_def_ = df_p[ ( df_p[ "defensiveTeam" ] == s_team ) & \
                ( df_p[ "gameId" ].isin( game_ids ) ) ]
list_all_def_plays = df_def_[ "playId" ].unique()

if all_players:

    print("No player_id specified, pulling all defensive players from **TEAM**")
    player_ids = []

else:

    # pull player data based on player_id
    row_p = df_ps[ df_ps[ "nflId" ] == player_id ]

    # print player name, player position
    print(f"{row_p['displayName'].values[0]} ({player_id}), " \
          f"plays {row_p['position'].values[0]}")

if set(list_played_plays).issubset(list_all_def_plays):

    participated_play_count = len(list_played_plays)
    total_def_play_count = len(list_all_def_plays)
    if all_games:
        print(f"Found games: {game_ids}")
    print(f"Participated in {participated_play_count} out " \
          f"of {total_def_play_count} defensive plays")

else:
    print("No defensive plays found")
    sys.exit(0)

# how many times did this player initate a pre-snap defensive movement?

# how many plays were offensive success vs. defensive success? (assign a score)
