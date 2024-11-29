# script and library to analyze plays

import pandas as pd
import numpy as np
import math

from scipy.spatial import distance

import sys

### FUNCTIONS ###

def get_frame_id_for_event(df, event_name):
    frame_id = -1
    event_row = df[ df[ "event" ] == event_name ]
    if not event_row.empty:
        frame_id = event_row["frameId"].values[0]
    return frame_id

def count_frames_between_events(df, event_name1, event_name2):
    frame_count = 0
    return frame_count

def get_top_speed_from_player_frames(df):
    fast_idx = df['s'].idxmax()
    fastest_row = df.loc[ fast_idx ]
    return round(fastest_row['s'],2), fastest_row['nflId'], fastest_row['frameId']

def get_distance_traveled_from_player_frames(df):
    sum_dist = df['dis'].sum()
    return round(sum_dist,2)

def get_player_name_by_id(df_players, player_id):
    player_row = df_players[ df_players["nflId"] == player_id ]
    return player_row["displayName"].values[0]

def get_player_info_by_name_at_frame(df, player_name):
    row = df[
        (df["displayName"] == player_name)
    ]
    return row

def get_player_info_by_id_at_frame(df, player_id):
    row = df[
        (df["nflId"] == player_id)
    ]
    return row

def get_player_distance_at_frame(df, player1, player2):

    p1_row = df[ df["displayName"] == player1 ]
    p2_row = df[ df["displayName"] == player2 ]

    p1_x = p1_row['x'].values[0]
    p1_y = p1_row['y'].values[0]
    p2_x = p2_row['x'].values[0]
    p2_y = p2_row['y'].values[0]

    dist = distance.euclidean((p1_x, p1_y), (p2_x, p2_y))
    return dist

def get_closest_player_to_point(x, y, df_players):

    min_distance = 200
    min_player_id = 0

    for i, p in df_players.iterrows():
        dist = distance.euclidean((x, y),(p["x"], p["y"]))
        if min_distance > dist:
            min_distance = dist
            min_player = p["nflId"]

    return [min_player, min_distance]

def get_closest_opposition(df, player_id):

    # pull the player's team
    player_df = df[ df["nflId"] == player_id ]
    club = player_df["club"].values[0]
    o_x = player_df["x"].values[0]
    o_y = player_df["y"].values[0]

    # grab all of the players from the other team
    def_players = df[ ~df["club"].isin([club, "football"]) ]

    min_distance = 200
    min_player_id = 0

    for i, p in def_players.iterrows():
        dist = distance.euclidean((o_x, o_y),(p["x"], p["y"]))
        #print(f"{p['displayName']}, {dist}")
        if min_distance > dist:
            min_distance = dist
            min_player_id = p["nflId"]

    return [min_player_id, min_distance]

def find_player_ids_by_position(df, position):

    position_rows = df[ df[ "position" ] == position ]
    player_id_list = position_rows[ "nflId" ].unique()
    return player_id_list

def find_player_id_by_closest_to_football(df, frame_id):

    # get the location of the football at the event
    football_row = df[
        (df['club'] == 'football') & \
        (df['frameId'] == frame_id)
    ]

    frame_df = df[ (df['frameId'] == frame_id ) ]
    #print(frame_df)

    if football_row.empty:
        raise ValueError(f"No football found at frame: {frame_id}")

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

def find_targeted_receiver_id(p_df, d_df):

    t_x = d_df["targetX"].values[0]
    t_y = d_df["targetY"].values[0]

    min_player = 0
    if not (math.isnan(t_x) or math.isnan(t_y)):
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

    df_tracking_unmerged = df_tracking[
        (df_tracking["playId"] == play_id) & \
        (df_tracking["gameId"] == game_id)
    ].copy()
    df_tracking_unmerged[[ "nflId" ]] = df_tracking_unmerged[[ "nflId" ]].fillna(-1)

    df_plays = pd.read_csv("data/kaggle/plays.csv")
    df_play_details = df_plays[
        (df_plays["playId"] == play_id) & \
        (df_plays["gameId"] == game_id)
    ]

    df_player_plays = pd.read_csv("data/kaggle/player_play.csv")
    df_player_play_details = df_player_plays[
        (df_player_plays[ "playId" ] == play_id) & \
        (df_player_plays[ "gameId" ] == game_id)
    ]

    df_players = pd.read_csv("data/kaggle/players.csv")
    df_players.loc[-1] = { 'nflId': -1, 'position': 'football' }
    df_players.index = df_players.index + 1
    df_players = df_players.sort_index()

    # merge player positions into tracking data
    df_player_positions = df_players[[ "nflId", "position" ]]
    df_play_tracking = df_tracking_unmerged.merge(df_player_positions, on=['nflId'])

    # print events log
    df_events = df_play_tracking[[ "frameId", "event" ]].dropna()
    df_events = df_events.drop_duplicates()

    print(df_events.to_string(index=False))
    print()

    print(df_play_details["playDescription"].values[0])
    print()

    expected_points = round(df_play_details['expectedPoints'].values[0],2)
    print(f"Expected Points:       {expected_points}")
    points_added = round(df_play_details['expectedPointsAdded'].values[0],2)
    print(f"Expected Points Added: {points_added}")
    offense_formation = df_play_details['offenseFormation'].values[0]
    print(f"Offense Formation:     {offense_formation}")
    receiver_alignment = df_play_details['receiverAlignment'].values[0]
    print(f"Receiver Alignment:    {receiver_alignment}")
    pass_coverage = df_play_details['pff_passCoverage'].values[0]
    print(f"Pass Coverage:         {pass_coverage}")
    print()

    is_pass_play = False
    is_run_play  = False

    # is this play a run, pass or other?

    pass_forward_frame_id = get_frame_id_for_event(df_play_tracking, "pass_forward")
    pass_shovel_frame_id = get_frame_id_for_event(df_play_tracking, "pass_shovel")
    handoff_frame_id = get_frame_id_for_event(df_play_tracking, "handoff")

    # check if this is a pass play
    if (handoff_frame_id > 0):
        is_run_play = True
        frame_id = handoff_frame_id
    elif (pass_forward_frame_id > 0):
        is_pass_play = True
        frame_id = pass_forward_frame_id
    elif (pass_shovel_frame_id > 0):
        is_pass_play = True
        frame_id = pass_shovel_frame_id

    df_frame = df_play_tracking[ df_play_tracking["frameId"] == frame_id ]
    qb_player_ids = find_player_ids_by_position(df_frame, "QB")
    passer_id = qb_player_ids[0]

    if is_pass_play:
        ballcarrier_id = find_targeted_receiver_id( df_play_tracking, df_play_details )
    else:
        rb_ids = find_player_ids_by_position( df_frame, "RB" )
        ballcarrier_id = rb_ids[0]

    passer_name = get_player_name_by_id( df_players, passer_id )
    if ballcarrier_id != 0:
        ballcarrier_name = get_player_name_by_id( df_players, ballcarrier_id )
    else:
        ballcarrier_name = "no receiver"

    if is_pass_play:
        events = [ "pass_forward", "pass_arrived" ]
    elif is_run_play:
        events = [ "handoff", "tackle" ]

    print(f"Before the snap")

    set_frame_id = get_frame_id_for_event(df_events, "line_set")
    snap_frame_id = get_frame_id_for_event(df_events, "ball_snap")

    df_pre_snap = df_play_tracking[ ( df_play_tracking[ "frameId" ] >= set_frame_id ) & \
                                    ( df_play_tracking[ "frameId" ] <= snap_frame_id )
                                  ]

    offense_team = df_play_details[ "possessionTeam" ].values[0]
    offense_players_pre_snap = df_pre_snap[ df_pre_snap[ "club" ] == offense_team ]
    spd, p_id, f_id = get_top_speed_from_player_frames(offense_players_pre_snap)
    name = get_player_name_by_id( df_players, p_id )
    print(f"  Fastest offensive player: {name}, {spd} yd/s at frame {f_id}")
    off_distance_traveled = get_distance_traveled_from_player_frames(offense_players_pre_snap)
    print(f"  Offense traveled a total of {off_distance_traveled} yds")

    defense_team = df_play_details[ "defensiveTeam" ].values[0]
    defense_players_pre_snap = df_pre_snap[ df_pre_snap[ "club" ] == defense_team ]
    spd, p_id, f_id = get_top_speed_from_player_frames(defense_players_pre_snap)
    name = get_player_name_by_id( df_players, p_id )
    print(f"  Fastest defensive player: {name} at {spd} yd/s at frame {f_id}")
    def_distance_traveled = get_distance_traveled_from_player_frames(defense_players_pre_snap)
    print(f"  Defense traveled a total of {def_distance_traveled} yds")

    print()

    for e in events:

        frame_id = get_frame_id_for_event(df_events, e)
        f = df_play_tracking[ df_play_tracking["frameId"] == frame_id ]

        if f.empty:
            continue

        print(f"Event \"{e}\" at frame {frame_id}")

        ballcarrier_line = get_player_info_by_name_at_frame(f, ballcarrier_name)
        reception_defender_id, defender_dist = get_closest_opposition(f, ballcarrier_line["nflId"].values[0])
        defender_name = get_player_name_by_id( df_players, reception_defender_id )
        rounded_defender_dist = round(defender_dist, 2)

        if ballcarrier_name != "no receiver":
            player_dist = round(get_player_distance_at_frame(f, passer_name, ballcarrier_name), 2)
            #player_dist = round(player_dist, 2)
            print(f"  Passer {passer_name} to receiver {ballcarrier_name} distance: {player_dist}")
            print(f"  Nearest defender {defender_name} is {rounded_defender_dist} from receiver")
            print()
