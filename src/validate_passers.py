import analyze_play as ap

import pandas as pd
import math
import sys

def get_player_position( player_id ):
    pass

def shorten_player_name( player_name ):
    substrings = player_name.split(" ")
    first_initial = substrings[0][0]
    last_name = substrings[-1]
    return first_initial + "." + last_name

def validate_passer_by_description( player_row, detailed_play_row ):

    player_name = player_row[ "displayName" ].values[0]
    short_name = shorten_player_name(player_name)

    play_detail = detailed_play_row["playDescription"].values[0]
    match_text = f"{short_name} pass"

    return_value = 0
    if match_text in play_detail:
        return_value = 1
    else:
        play_id = detailed_play_row["playId"].values[0]
        print(f"{play_id}\tp: {player_name}\t{play_detail[:50]}")

    return return_value

tracking_file = "data/kaggle/tracking_week_1.csv"
df_tracking = pd.read_csv(tracking_file)

df_plays = pd.read_csv("data/kaggle/plays.csv")
df_players = pd.read_csv("data/kaggle/players.csv")

total_passes = 0

successful_validation = 0
unsuccessful_validation = 0

game_ids = df_tracking[ "gameId" ].unique()

#game_ids = game_ids[:1]
#game_ids = [ 2022091101, 2022091102, 2022091103 ]

for g in game_ids:

    df_game = df_tracking[
                (df_tracking["gameId"] == g ) &\
                (df_tracking["event"] == "pass_forward")
    ]

    play_ids = df_game["playId"].unique()
    total_passes += len(play_ids)
    #first_five_play_ids = play_ids[:5]

    for i in play_ids:

        df_play_frames = df_game[ df_game["playId"] == i ]
        df_play_detailed = df_plays[
            (df_plays["gameId"] == g) & \
            (df_plays["playId"] == i)
        ]

        passer_id = ap.find_passer_id_by_closest_to_football(df_play_frames)
        passer_name = ap.get_player_name_by_id(df_players, passer_id)

        # get player row from dataframe
        passer_row = df_players[ df_players["nflId"] == passer_id ]
        validate_result = validate_passer_by_description(passer_row, df_play_detailed)

        successful_validation += validate_result
        if validate_result == 0:
            unsuccessful_validation += 1

print()
print(f"Total passes found: {total_passes}; "
      f"matching passers = {successful_validation}; non-matching passers = {unsuccessful_validation}")
