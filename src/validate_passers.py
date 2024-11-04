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

    return return_value

try:
    game_id = int(sys.argv[1])
except:
    print("Invalid game id format")
    sys.exit(1)

tracking_file = "data/kaggle/tracking_week_8.csv"
df_tracking = pd.read_csv(tracking_file)

df_plays = pd.read_csv("data/kaggle/plays.csv")
df_players = pd.read_csv("data/kaggle/players.csv")

df_game = df_tracking[
            (df_tracking["gameId"] == game_id ) &\
            (df_tracking["event"] == "pass_forward")
]

play_ids = df_game["playId"].unique()
first_five_play_ids = play_ids[:5]

successful_validation = 0
unsuccessful_validation = 0

for i in play_ids:

    df_play_frames = df_game[ df_game["playId"] == i ]
    df_play_detailed = df_plays[
        (df_plays["gameId"] == game_id) & \
        (df_plays["playId"] == i)
    ]

    passer_id = ap.find_passer_id(df_play_frames)
    passer_name = ap.get_player_name_by_id(df_players, passer_id)

    # get player row from dataframe
    passer_row = df_players[ df_players["nflId"] == passer_id ]

    n,d = ap.get_closest_defender(df_play_frames, passer_name)
    pass_outcome = df_play_detailed["passResult"].values[0]
    pass_d = round(d, 2)

    rec_d = float('nan')
    targeted_receiver_id = ap.find_targeted_receiver_id(df_play_frames, df_play_detailed)
    if targeted_receiver_id != 0:
        targeted_receiver_name = ap.get_player_name_by_id(df_players, targeted_receiver_id)
        n,rec_d = ap.get_closest_defender(df_play_frames, targeted_receiver_name)
        rec_d = round(rec_d, 2)

    validate_result = validate_passer_by_description(passer_row, df_play_detailed)

    successful_validation += validate_result
    if validate_result == 0:
        unsuccessful_validation += 1
        print(f"{df_play_detailed['playId'].values[0]}: "
              f"{df_play_detailed['playDescription'].values[0]}")

    print(f"{i}: {passer_name}; pass sep: {pass_d}; rec sep: {rec_d}; "
          f"res: {pass_outcome}; {validate_result}")

#print("Hello World")
print()
print(f"Total passes found: {len(play_ids)}; "
      f"valid passers = {successful_validation}; invalid passers = {unsuccessful_validation}")
