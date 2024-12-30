import pandas as pd
import analyze_play as ap

import sys
import math

from itertools import groupby
from operator import itemgetter

### CONSTANTS ###

ap.DATA_DIR = "data/kaggle"

# Set thresholds - the player has to maintain t_speed for at least t_time
# to qualify as a motion event
SPEED_THRESHOLD = 0.9  # yards / sec
TIME_THRESHOLD  = 0.5  # seconds (multiply * 10 for frame count)

### FUNCTIONS ###

def get_opposite_dir(direction):

    opposite = ""

    if direction == "right":
        opposite = "left"
    elif direction == "left":
        opposite = "right"
    elif direction == "up":
        opposite = "down"
    elif direction == "down":
        opposite = "up"
    elif direction == "forward":
        opposite = "back"
    elif direction == "back":
        opposite = "forward"

    return opposite

def get_min_frame_from_events( df, l_events ):
    min_frame = 500
    for e in l_events:
        frame = int(ap.get_frame_id_for_event(df, e))
        if (frame > - 1)  & (frame < min_frame):
            min_frame = frame
    return min_frame

def get_max_frame_from_events( df, l_events ):
    max_frame = 0
    for e in l_events:
        frame = int(ap.get_frame_id_for_event(df, e))
        if frame > max_frame:
            max_frame = frame
    return max_frame

def get_presnap_dataframe( df, start_frame, end_frame ):
    df_ = df[ ( df[ "frameId" ] >= start_frame ) & \
              ( df[ "frameId" ] <= end_frame ) ]
    return df_

def get_tracking_info_for_player_frame(df_presnap, player_id, frame_id):

    player_frame_row = df_presnap[ ( df_presnap[ "nflId" ] == player_id ) & \
                                   ( df_presnap[ "frameId" ] == frame_id ) ]
    return player_frame_row

def get_player_ids(df):
    return df["nflId"].unique()

def get_general_direction_and_offset(vector_x, vector_y, play_direction):

    abs_vector_x = abs( vector_x )
    abs_vector_y = abs( vector_y )

    f_horizontal = ( abs_vector_x >  abs_vector_y )
    f_vertical   = ( abs_vector_x <= abs_vector_y )

    f_x_neg = ( vector_x < abs_vector_x )
    f_y_neg = ( vector_y < abs_vector_y )

    angle_rad = math.atan2( vector_y, vector_x )
    angle_deg = math.degrees(angle_rad)
    general_dir = ""

    if f_horizontal:
        if f_x_neg:
            general_dir = "left"
            if angle_deg < 0:
                offset = 180 + angle_deg
            else:
                offset = 180 - angle_deg
        else:
            general_dir = "right"
            offset = angle_deg
    else:
        if f_y_neg:
            general_dir = "down"
            offset = 90 + angle_deg
        else:
            general_dir = "up"
            offset = 90 - angle_deg

    return (general_dir, offset)

def get_motion_event_frames_by_player(df, p_id):

    l_grouped_frames = []

    # get all frames for player above threshold speed
    df_ = df[ ( df[ "nflId" ] == p_id ) & \
              ( df[ "s" ] >= SPEED_THRESHOLD ) ]

    if (len(df_)) > 0:

        frames = df_[ "frameId" ].unique()
        #print(frames)

        # group frames by consecutive numbers
        for k, g in groupby(enumerate(frames), lambda i_x: i_x[0] - i_x[1]):
            l_group = list(map(itemgetter(1), g))
            if len(l_group) > (TIME_THRESHOLD * 10):
                l_grouped_frames.append(l_group)

    # return list of frame id's
    return l_grouped_frames

def summarize_motion_event(df, l_frames, player_id, is_def):

    f_start = l_frames[0]
    f_end = l_frames[-1]

    motion_time = (f_end - f_start) / 10

    start_row = get_tracking_info_for_player_frame( df, player_id, f_start )
    end_row = get_tracking_info_for_player_frame( df, player_id, f_end )

    name = ap.get_player_name_by_id(df, player_id)

    s_play_dir = start_row["playDirection"].values[0]

    vector_x = end_row["x"].values[0] - start_row["x"].values[0]
    vector_y = end_row["y"].values[0] - start_row["y"].values[0]

    motion_dir, dir_offset = get_general_direction_and_offset(vector_x, vector_y, s_play_dir)

    if abs(dir_offset) > 45:
        print(f"WARN: {name:17} ({p}): {f_start:3} - {f_end:3}; {motion_dir:6} {dir_offset}")

    total_distance = math.sqrt((vector_x ** 2) + (vector_y ** 2))
    abs_speed = total_distance / motion_time

    if is_def:
        team_dir = get_opposite_dir(s_play_dir)
    else:
        team_dir = s_play_dir

    return [ f_start, f_end, vector_x, vector_y, motion_dir, dir_offset,
             team_dir, total_distance, abs_speed ]


def get_motion_events( game_id, play_id ):

    df_f, df_d = ap.load_tracking_from_game_and_play(game_id, play_id)
    df_pp = pd.read_csv(f"{ap.DATA_DIR}/player_play.csv")

    defense_team = df_d["defensiveTeam"].values[0]
    print(df_d["playDescription"].values[0])
    #print(df_f.shape)

    start_events = [ "line_set", "man_in_motion" ]
    end_events = [ "ball_snap" ]

    presnap_start = get_min_frame_from_events(df_f, start_events)
    presnap_end = get_max_frame_from_events(df_f, end_events)
    print(f"{presnap_start}, {presnap_end}")

    df_pre = get_presnap_dataframe(df_f, presnap_start, presnap_end)
    #print(df_pre)

    p_ids = get_player_ids(df_pre)

    l_motions = []
    motion_idx = 11

    for p in p_ids:

        # nflId is nan for the football, so we can ignore it for the loop
        if math.isnan(p):
            continue

        row_pp = df_pp[ ( df_pp[ "gameId" ] == game_id ) & \
                        ( df_pp[ "nflId" ] == p ) ]
        team = row_pp[ "teamAbbr" ].values[0]
        is_defense = (defense_team == team)

        t_frames = get_motion_event_frames_by_player(df_pre, p)
        for l in range(len(t_frames)):

            player_stats = [ game_id, play_id, p, motion_idx, team, is_defense ]

            #l_frames = t_frames[l]
            l_stats = summarize_motion_event( df_pre, t_frames[l], p, is_defense )
            l_motions.append( player_stats + l_stats )

            motion_idx += 1

    columns = [ "gameId", "playId", "nflId", "motionEventId", "teamAbbr", "isDefense", "startFrameId",
                "endFrameId", "vectorX", "vectorY", "motionDir", "dirOffest", "teamDir", "totalDistance",
                "absSpeed" ]

    return pd.DataFrame( l_motions, columns=columns )



### MAIN ###

if (len(sys.argv) < 3):
    print("Specify gameId and playId")
    sys.exit(1)

try:
    g_id = int(sys.argv[1])
except:
    print("Invalid game id format")
    sys.exit(1)

try:
    p_id = int(sys.argv[2])
except:
    print("Invalid play id format")
    sys.exit(1)

df_out = get_motion_events( g_id, p_id )
print(df_out)
