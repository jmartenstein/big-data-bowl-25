import pandas as pd
import analyze_play as ap
import sklearn.metrics as ms

import argparse
import random
import sys


### FUNCTIONS ###

def get_pass_motion_coverage_for_play( df_row ):

    opposite_team_dir = ap.get_opposite_dir( df_row[ "teamDir" ] )
    defense_player_dir = df_row[ "motionDir" ]

    return (opposite_team_dir == defense_player_dir)

def get_isdropback_dataframe( df_ps, df_pp, l_games, player_id ):

    # get dataframe with plays and dropback
    df_game_plays = df_ps[ ( df_ps[ "gameId" ].isin(l_games) ) ]
    df_dropback_plays = df_game_plays[[ "gameId", "playId", "isDropback" ]]

    # get participating plays for player
    df_participating_plays = df_pp[ ( df_pp[ "gameId" ].isin(l_games) ) & \
                                    ( df_pp[ "nflId"  ] == int(player_id) ) ]
    #print(f"Found {len(df_participating_plays)} plays for {p_id}")
    df_merged_game_plays = df_participating_plays.merge( df_game_plays, on=["gameId", "playId"] )

    return df_merged_game_plays[[ "gameId", "playId", "nflId", "isDropback" ]].copy()

def get_motionplays_dataframe(df_motion, player_id):

    # get significant motion events for player in game
    df_pm = df_motion[ df_motion[ "nflId" ] == int(player_id) ].copy()
    df_pm.sort_values( by=['playId', 'totalDistance','nflId','gameId'],
                       axis=0, ascending=True, inplace=True)
    df_pm.drop_duplicates(subset=['gameId', 'playId', 'nflId'], inplace=True, keep='last')

    return df_pm

def get_merged_motion_and_dropback(df_ps, df_pp, df_mp, l_games, player_id):

    df_plays_isdropback = get_isdropback_dataframe( df_ps, df_pp, l_games, player_id)
    df_player_motion = get_motionplays_dataframe(df_mp, player_id)

    #print(f"id: {player_id} dropback: {df_plays_isdropback.shape}, motion: {df_player_motion.shape}")

    return df_plays_isdropback.merge( df_player_motion, on=['gameId', 'playId', 'nflId'],
                                      how='left' )

def compare_dropbacks_and_pass_motions( df_mp, player_id ):

    test_col   = df_mp[[ "isPassMotionCoverage" ]]
    result_col = df_mp[[ "isDropback" ]]

    acc = ms.accuracy_score(test_col, result_col).round(4)
    pre = ms.precision_score(test_col, result_col).round(4)
    rec = ms.recall_score(test_col, result_col, zero_division=0).round(4)
    f1 =  ms.f1_score(test_col, result_col).round(4)

    tn, fp, fn, tp = ms.confusion_matrix(test_col, result_col).ravel()

    #print(f"{p_id} - plays: {len(df_merged_plays)}, acc: {acc}, f1: {f1}; tn: {tn}, fp: {fp}, fn: {fn}, tp: {tp}")
    return [ int(player_id), len(df_merged_plays), tn, fp, fn, tp, acc, pre, rec, f1 ]


### MAIN ###

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

l_game_strings = s_game.split(",")
l_games = list(map(int, l_game_strings))

# if no player is specified, then pull all of the defensive players
if s_player:
    player_ids = [ int(s_player) ]
else:
    player_ids = ap.get_defensive_players_in_games_by_team(l_games, s_team)

motion_filename      = f"{ap.PROCESSED_DATA_DIR}/motion.20250101.185127.csv"
plays_filename       = f"{ap.RAW_DATA_DIR}/plays.csv"
player_play_filename = f"{ap.RAW_DATA_DIR}/player_play.csv"

df_motion      = pd.read_csv(motion_filename)
df_plays       = pd.read_csv(plays_filename)
df_player_play = pd.read_csv(player_play_filename)

l_players = []

for p in player_ids:

    df_merged_plays = get_merged_motion_and_dropback(df_plays, df_player_play,
                                                     df_motion, l_games, p)
    list_participating_plays = df_merged_plays[ "playId" ].unique()

    df_merged_plays["isPassMotionCoverage"] = df_merged_plays.apply(
        get_pass_motion_coverage_for_play, axis=1 )

    #print(df_merged_plays.head())
    #print(df_merged_plays.columns)
    #print(df_merged_plays[[ "gameId", "playId", "teamDir", "motionDir", "isPassMotionCoverage", "isDropback" ]])
    #print()

    #print(len(df_merged_plays))
    if len(df_merged_plays) > 1:
        pass_row = compare_dropbacks_and_pass_motions( df_merged_plays, p )
        l_players.append(pass_row)
        #print(pass_row)

col_names = [ "nflId", "plays", "tn", "fp", "fn", "tp", "acc", "pre", "rec", "f1" ]
df_pass_reads = pd.DataFrame(l_players, columns=col_names)

df_pass_reads.sort_values(by=["tp", "tn"], inplace=True, ascending=False)
print(df_pass_reads.to_string(index=False))
