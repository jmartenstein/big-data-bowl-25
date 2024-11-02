# Code to analyze a play from 09/11/2022 between TB and DAL

import pandas as pd
import numpy as np

from scipy.spatial import distance

import sys

### FUNCTIONS ###

def get_frame_id_for_event(df, event_name):
    event_row = df[ df[ "event" ] == event_name ]
    frame_id = event_row["frameId"].values[0]
    return frame_id

def get_player_info_at_frame(df, player_name):
    row = df[
        (df["displayName"] == player_name)
    ]
    return row

def get_closest_player_to_point(x, y, df_players):

    min_distance = 200
    min_player = ""

    for i, p in df_players.iterrows():
        dist = distance.euclidean((x, y),(p["x"], p["y"]))
        if min_distance > dist:
            min_distance = dist
            min_player = p["displayName"]

    return [min_player, min_distance]

def get_closest_defender(df, player_name):

    # pull the player's team
    player_df = df[ df["displayName"] == player_name ]
    club = player_df["club"].values[0]
    o_x = player_df["x"].values[0]
    o_y = player_df["y"].values[0]

    # grab all of the players from the other team
    def_players = df[ ~df["club"].isin([club, "football"]) ]

    min_distance = 200
    min_player = ""

    for i, p in def_players.iterrows():
        dist = distance.euclidean((o_x, o_y),(p["x"], p["y"]))
        #print(f"{p['displayName']}, {dist}")
        if min_distance > dist:
            min_distance = dist
            min_player = p["displayName"]

    return [min_player, min_distance]

def find_passer_name(df):

    # look for a frame with a "pass_forward" event
    frame_id = get_frame_id_for_event(df, "pass_forward")

    # get the location of the football at the event
    football_row = df[
        (df['club'] == 'football') & \
        (df['frameId'] == frame_id)
    ]
    f_x = football_row['x'].values[0]
    f_y = football_row['y'].values[0]

    # get the players from the list that are not the football
    player_rows = df[
        (df['club'] != 'football') & \
        (df['frameId'] == frame_id)
    ]

    # find the closest player to the football (ASSUMPTION: this is the QB)
    min_player, distance = get_closest_player_to_point(f_x, f_y, player_rows)

    return min_player

def find_targeted_receiver_name(p_df, d_df):

    t_x = d_df["targetX"].values[0]
    t_y = d_df["targetY"].values[0]

    min_player, distance = get_closest_player_to_point(t_x, t_y, p_df)

    return min_player

### MAIN ###

if __name__  == '__main__':

    if (len(sys.argv) < 3):
        print("Specify gameId and playId")
        sys.exit(1)

    try:
        game_id = int(sys.argv[1])
    except:
        print("Invalid game id format")
        sys.exit(1)

    try:
        play_id = int(sys.argv[2])
    except:
        print("Invalid play id format")
        sys.exit(1)

    tracking_file = "data/kaggle/tracking_week_1.csv"
    df_tracking = pd.read_csv(tracking_file)

    df_play_tracking = df_tracking[
        (df_tracking["playId"] == play_id) & \
        (df_tracking["gameId"] == game_id)
    ]

    df_plays = pd.read_csv("data/kaggle/plays.csv")
    df_play_details = df_plays[
        (df_plays["playId"] == play_id) & \
        (df_plays["gameId"] == game_id)
    ]

    #print(df_play_tracking.shape)

    # print events log
    df_events = df_play_tracking[[ "frameId", "event" ]].dropna()
    df_events = df_events.drop_duplicates()

    print(df_events)
    print()

    passer_name = find_passer_name( df_play_tracking )
    receiver_name = find_targeted_receiver_name( df_play_tracking, df_play_details )

    events = [ "pass_forward", "pass_arrived" ]
    players = [passer_name, receiver_name]

    for e in events:

        frame_id = get_frame_id_for_event(df_events, e)
        f = df_play_tracking[ df_play_tracking["frameId"] == frame_id ]

        for p in players:
            player_line = get_player_info_at_frame(f, p)
            player_info = get_closest_defender(f, p)
            print(f"{frame_id} ({e}): {p} pos {player_line['x'].values[0]},"
                  f"{player_line['y'].values[0]} spd {player_line['s'].values[0]}; "
                  f"near def: {player_info[0]}, {round(player_info[1],2)}")

        print()
