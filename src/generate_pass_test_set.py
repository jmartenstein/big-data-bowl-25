import pandas as pd
import math
import sys

import analyze_play as ap

def is_passer_from_frames(df, nfl_id):
    frame_id = ap.get_frame_id_for_event(df, "pass_forward")
    if (frame_id < 0):
        frame_id = ap.get_frame_id_for_event(df, "pass_shovel")
    passer_id = ap.find_player_id_by_closest_to_football(df, frame_id)
    return (passer_id == nfl_id)

def is_receiver_from_frames(df, nfl_id):
    frame_id = ap.get_frame_id_for_event(df, "pass_outcome_caught")
    if frame_id < 0:
        frame_id = ap.get_frame_id_for_event(df, "pass_arrived")
    receiver_id = ap.find_player_id_by_closest_to_football(df, frame_id)
    return (receiver_id == nfl_id)

# load game tracking data
df_tr = pd.read_csv("data/kaggle/tracking_week_1.csv")

# get unique list of week 1 games from tracking data
series_games_week1 = df_tr[ "gameId" ]
list_games_week1 = series_games_week1.unique()

# load plays result data, limit to week 1
df_ps = pd.read_csv("data/kaggle/plays.csv")
df_ps_week1 = df_ps[ df_ps["gameId"].isin(list_games_week1) ]

# filter only the gameId and playId (indices), and the pass result
df_pr_week1 = df_ps_week1[[ "gameId", "playId", "passResult" ]]

# merge pass result with tracking data, and limit only to completed passes
df_merge = df_tr.merge(df_pr_week1, on=['gameId','playId'])
df_cp_week1 = df_merge[ df_merge["passResult"] == "C" ].copy()

list_test_set = []

for game in list_games_week1:

    # get a list of plays for the game
    df_game_plays = df_cp_week1[ df_cp_week1["gameId"] == game ].copy()
    series_plays = df_game_plays["playId"]
    list_plays = series_plays.unique()

    print(f"Analyzing game: {game}")

    for play in list_plays:

        # isolate frame data for play
        df_play_frames = df_game_plays[ ( df_game_plays["playId"] == play ) ].copy()

        series_players = df_play_frames[ "nflId" ].dropna()
        list_players = series_players.unique()
        for player in list_players:

            # find passer in frame data
            is_passer = is_passer_from_frames(df_play_frames, player)

            # find receiver in frame data
            is_receiver = is_receiver_from_frames(df_play_frames, player)

            player_row = {
                'gameId': game,
                'playId': play,
                'nflId': player,
                'isPasser': is_passer,
                'isReceiver': is_receiver
            }

            list_test_set.append(player_row)

df_test_set = pd.DataFrame(list_test_set)
df_test_set.sort_values(by=['gameId','playId','nflId'],inplace=True)

header = [ "gameId", "playId", "nflId", "isPasser", "isReceiver" ]
df_test_set.to_csv('data/pass_test_set.csv', columns=header, index=False)

