import pandas as pd
import analyze_play as ap
import sklearn.metrics as ms
import numpy as np

from sklearn.metrics import roc_auc_score

import argparse
import datetime
import glob
import random
import sys


### FUNCTIONS ###

def get_passread_filename(game_id=''):

    now = datetime.datetime.now()

    s_date = now.strftime("%Y%m%d")
    s_time = now.strftime("%H%M%S")

    if game_id:
        s_prefix = f"passread.{game_id}"
    else:
        s_prefix = "passread"

    return f"{s_prefix}.{s_date}.{s_time}.csv"

def motiondir_to_int( df_row ):

    if (df_row[ "motionDirRelativeToScrimmage" ] == "back"):
        return 1
    else:
        return 0

def isdropback_to_int( df_row ):

    if (df_row["isDropback"]):
        return 1
    else:
        return 0

def get_pass_motion_coverage_for_play( df_row ):

    relative_dir = df_row[ "motionDirRelativeToScrimmage" ]
    return (relative_dir == "back")

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
    df_pm.sort_values( by=['playId', 'totalDistance', 'nflId', 'gameId'],
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

    cm_test_col   = df_mp[[ "isPassMotionCoverage" ]]
    cm_result_col = df_mp[[ "isDropback" ]]

    acc = ms.accuracy_score(cm_test_col, cm_result_col).round(4)
    pre = ms.precision_score(cm_test_col, cm_result_col, zero_division=0).round(4)
    rec = ms.recall_score(cm_test_col, cm_result_col, zero_division=0).round(4)
    f1 =  ms.f1_score(cm_test_col, cm_result_col, zero_division=0).round(4)

    #print(f"{player_id} - plays: {len(df_merged_plays)}, cov: {len(test_col)}, dropbacks: {len(result_col)}")
    matrix_array = ms.confusion_matrix(cm_test_col, cm_result_col).ravel()
    if (len(matrix_array) == 4):
        tn, fp, fn, tp = matrix_array
        if (tp + fn) > 0:
            tpr = round(tp / (tp + fn), 4)
        else:
            tpr = np.nan
        if (tn + fp) > 0:
            fpr = round(tn / (tn + fp), 4)
        else:
            fpr = np.nan
    else:
        print(f"WARN: player {player_id} has incorrect shape of matrix: {matrix_array}")
        tn, fp, fn, tp = [len(cm_test_col), 0, 0, 0]
        tpr, fpr = [ 0.0, 1.0 ]

    auc_test_col = df_mp[ "motionDirToInt" ]
    auc_result_col = df_mp[ "isDropbackToInt" ]

    try:
        auc = roc_auc_score(auc_test_col, auc_result_col)
    except ValueError:
        auc = 0

    return [ int(player_id), len(df_merged_plays), tn, fn, fp, tp, tpr, fpr, acc, pre, rec, f1, auc ]


### MAIN ###

# parse arguments for game_id and player_id
parser = argparse.ArgumentParser( description='Analyze how well defensive players \
                                               can read an offense' )
parser.add_argument( '-g', '--game',    help='Specify game_id (leave blank to analyze \
                                              all games in weeks 1 - 6)' )
parser.add_argument( '-p', '--player',  help='Specify player_id (leave blank to \
                                              analyze all defensive players per game)' )
parser.add_argument( '-t', '--team',    help='If no player_id, get all defensive players' \
                                             'from team' )
parser.add_argument( '-o', '--outfile', action='store_true',
                     help='If set, write output to file')
args = vars( parser.parse_args() )

s_team = args["team"]
s_player = args["player"]
s_game = args["game"]
f_outfile = args["outfile"]

l_game_strings = s_game.split(",")
l_games = list(map(int, l_game_strings))

# if no player is specified, then pull all of the defensive players
if s_player:
    player_ids = [ int(s_player) ]
else:
    player_ids = ap.get_defensive_players_in_games_by_team(l_games, s_team)

motion_filename      = f"{ap.PROCESSED_DATA_DIR}/motion.week4.20250105*"
plays_filename       = f"{ap.RAW_DATA_DIR}/plays.csv"
player_play_filename = f"{ap.RAW_DATA_DIR}/player_play.csv"
players_filename     = f"{ap.RAW_DATA_DIR}/players.csv"

motion_files_found = glob.glob(motion_filename)
if len(motion_files_found) > 1:
    print(f"ERROR: Motion file {motion_filename} is not specific enough; " \
          f"found {len(motion_files_found)} files")
    sys.exit(1)

df_motion      = pd.read_csv(motion_files_found[0])
df_plays       = pd.read_csv(plays_filename)
df_player_play = pd.read_csv(player_play_filename)
df_players     = pd.read_csv(players_filename)

l_players = []

for p in player_ids:

    df_merged_plays = get_merged_motion_and_dropback(df_plays, df_player_play,
                                                     df_motion, l_games, p)
    list_participating_plays = df_merged_plays[ "playId" ].unique()

    df_merged_plays["isPassMotionCoverage"] = df_merged_plays.apply(
        get_pass_motion_coverage_for_play, axis=1 )

    df_merged_plays["motionDirToInt"]  =  df_merged_plays.apply(motiondir_to_int, axis = 1)
    df_merged_plays["isDropbackToInt"] =  df_merged_plays.apply(isdropback_to_int, axis = 1)

    #print(df_merged_plays.head())
    #print(df_merged_plays.columns)
    #print(df_merged_plays[[ "gameId", "playId", "teamDir", "motionDir", "isPassMotionCoverage", "isDropback" ]])
    #print()

    #print(len(df_merged_plays))
    if len(df_merged_plays) > 1:
        pass_row = compare_dropbacks_and_pass_motions( df_merged_plays, p )
        l_players.append(pass_row)
        #print(pass_row)

col_names = [ "nflId", "plays", "tn", "fn", "fp", "tp", "tpr", "fpr", "acc", "pre", "rec", "f1", "auc" ]
df_pr_ = pd.DataFrame(l_players, columns=col_names)

# merge pass reads dataframe with subset of players dataframe
df_players_subset = df_players[[ "nflId", "displayName", "position" ]]
df_pass_reads = df_pr_.merge( df_players_subset, on=["nflId"] )

df_pass_reads.sort_values(by=["tp", "tn"], inplace=True, ascending=False)
merged_col_names = [ "displayName", "position" ] + col_names

df_out = df_pass_reads[ merged_col_names ]

if f_outfile:
    if len(l_games) > 1:
        outfile_name = get_passread_filename()
    else:
        outfile_name = get_passread_filename( l_games[0] )
    print(f"DataFrame (shape: {df_out.shape}) to file {outfile_name}")
    df_out.to_csv(f"data/processed/{outfile_name}", index=False)
else:
    print(df_out.to_string(index=False))
