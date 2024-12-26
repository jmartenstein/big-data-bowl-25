import pandas as pd
import analyze_play as ap

import sys
import math

from itertools import groupby
from operator import itemgetter

ap.DATA_DIR = "data/kaggle"

### FUNCTIONS ###

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

    general_dir = ""

    if f_horizontal:
        if f_x_neg:
            general_dir = "abs_left"
        else:
            general_dir = "abs_right"
    else:
        if f_y_neg:
            general_dir = "abs_down"
        else:
            general_dir = "abs_up"

    return (general_dir, 0.0)

def get_motion_event_frames_by_player(df, p_id, t_speed, t_time):

    l_grouped_frames = []

    # get all frames for player above threshold speed
    df_ = df[ ( df[ "nflId" ] == p_id ) & \
              ( df[ "s" ] >= t_speed ) ]

    if (len(df_)) > 0:

        frames = df_[ "frameId" ].unique()
        #print(frames)

        # group frames by consecutive numbers
        for k, g in groupby(enumerate(frames), lambda i_x: i_x[0] - i_x[1]):
            l_group = list(map(itemgetter(1), g))
            if len(l_group) > (t_time * 10):
                l_grouped_frames.append(l_group)

    # return list of frame id's
    return l_grouped_frames

### MAIN ###

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

df_f, df_d = ap.load_tracking_from_game_and_play(game_id, play_id)
df_pp = pd.read_csv(f"{ap.DATA_DIR}/player_play.csv")

print(df_d["playDescription"].values[0])
#print(df_f.shape)

start_events = [ "line_set", "man_in_motion" ]
end_events = [ "ball_snap" ]

presnap_start = get_min_frame_from_events(df_f, start_events)
presnap_end = get_max_frame_from_events(df_f, end_events)
print(f"{presnap_start}, {presnap_end}")

df_pre = get_presnap_dataframe(df_f, presnap_start, presnap_end)
#print(df_pre)

# Set thresholds - the player has to maintain t_speed for at least t_time
# to qualify as a motion event
t_speed = 0.9  # yards / sec
t_time  = 0.5  # seconds (multiply * 10 for frame count)

p_ids = get_player_ids(df_pre)

l_motions = []
motion_idx = 11

for p in p_ids:

    # nflId is nan for the football, so we can ignore it for the loop
    if math.isnan(p):
        continue

    t_frames = get_motion_event_frames_by_player(df_pre, p, t_speed, t_time)
    row_pp = df_pp[ ( df_pp[ "gameId" ] == game_id ) & \
                    ( df_pp[ "playId" ] == play_id) & \
                    ( df_pp[ "nflId" ] == p ) ]

    team = row_pp[ "teamAbbr" ].values[0]

    for l in range(len(t_frames)):

        l_frames = t_frames[l]
        f_start = l_frames[0]
        f_end = l_frames[-1]

        motion_time = (f_end - f_start) / 10

        start_row = get_tracking_info_for_player_frame( df_pre, p, f_start )
        end_row = get_tracking_info_for_player_frame( df_pre, p, f_end )

        s_play_dir = start_row["playDirection"].values[0]

        vector_x = end_row["x"].values[0] - start_row["x"].values[0]
        vector_y = end_row["y"].values[0] - start_row["y"].values[0]

        motion_dir, dir_offset = get_general_direction_and_offset(vector_x, vector_y, s_play_dir)

        total_distance = math.sqrt((vector_x ** 2) + (vector_y ** 2))
        abs_speed = total_distance / motion_time

        l_motions.append( [ game_id, play_id, p, team, motion_idx, f_start, f_end,
                            vector_x, vector_y, motion_dir, dir_offset, s_play_dir, total_distance,
                            abs_speed ] )
        motion_idx += 1

columns = [ "gameId", "playId", "nflId", "teamAbbr", "motionEventId", "startFrameId",
            "endFrameId", "vectorX", "vectorY", "motionDir", "dirOffest", "playDir", "totalDistance",
            "absSpeed" ]
df_out = pd.DataFrame( l_motions, columns=columns )
df_out.columns
print(df_out)
