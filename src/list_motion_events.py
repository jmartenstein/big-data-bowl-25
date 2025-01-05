import pandas as pd
import analyze_play as ap

import sys
import math

from datetime  import datetime
from itertools import groupby
from operator  import itemgetter

### CONSTANTS ###

ap.DATA_DIR = "data/kaggle"

# Set thresholds - the player has to maintain t_speed for at least t_time
# to qualify as a motion event
SPEED_THRESHOLD = 1.6  # yards / sec
TIME_THRESHOLD  = 0.5  # seconds (multiply * 10 for frame count)


### FUNCTIONS ###

def get_motion_event_filename(game_id=''):

    now = datetime.now()

    s_date = now.strftime("%Y%m%d")
    s_time = now.strftime("%H%M%S")

    if game_id:
        s_prefix = f"motion.{game_id}"
    else:
        s_prefix = "motion"

    return f"{s_prefix}.{s_date}.{s_time}.csv"

def get_plays_from_game( game_id ):

    plays_file = ap.DATA_DIR + "/plays.csv"
    df_all_plays = pd.read_csv(plays_file)

    df_game_plays = df_all_plays[ df_all_plays[ "gameId" ] == game_id ]

    return df_game_plays["playId"].unique()

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

    s_dir = ""
    i_dir = 0

    if f_horizontal:
        if f_x_neg:
            s_dir = "left"
            i_dir = 180
            if angle_deg < 0:
                offset = 180 + angle_deg
            else:
                offset = 180 - angle_deg
        else:
            s_dir = "right"
            offset = angle_deg
    else:
        if f_y_neg:
            s_dir = "down"
            i_dir = -90
            offset = 90 + angle_deg
        else:
            s_dir = "up"
            i_dir = 90
            offset = 90 - angle_deg

    return (s_dir, i_dir, round(offset, 4))

def get_motion_dir_relative_to_scrimmage(v_x, team_dir):

    result_val = False
    f_relative_dir = 1

    if (team_dir == "left") and (v_x > 0):
        f_relative_dir = -1

    if (team_dir == "right") and (v_x < 0):
        f_relative_dir = -1

    return f_relative_dir

def get_motion_event_frames_by_player(df, p_id):

    l_grouped_frames = []

    # get all frames for player above threshold speed
    df_ = df[ ( df[ "nflId" ] == p_id ) & \
              ( df[ "s" ] >= SPEED_THRESHOLD ) ]

    if (len(df_)) > 0:

        frames = df_[ "frameId" ].unique()

        # group frames by consecutive numbers
        for k, g in groupby(enumerate(frames), lambda i_x: i_x[0] - i_x[1]):
            l_group = list(map(itemgetter(1), g))
            if len(l_group) > (TIME_THRESHOLD * 10):
                l_grouped_frames.append(l_group)

    return l_grouped_frames

def summarize_motion_event(df, l_frames, player_id, los, is_def):

    f_start = l_frames[0]
    f_end = l_frames[-1]

    motion_time = (f_end - f_start) / 10

    start_row = get_tracking_info_for_player_frame( df, player_id, f_start )
    end_row   = get_tracking_info_for_player_frame( df, player_id, f_end )

    name = ap.get_player_name_by_id(df, player_id)

    s_play_dir = start_row["playDirection"].values[0]

    vector_x = round(end_row["x"].values[0] - start_row["x"].values[0], 4)
    vector_y = round(end_row["y"].values[0] - start_row["y"].values[0], 4)

    abs_vector_x = abs(vector_x)

    final_x = round(end_row["x"].values[0], 4)
    final_y = round(end_row["y"].values[0], 4)

    x_to_los = round(abs(los - final_x), 4)

    if is_def:
        team_dir = ap.get_opposite_dir(s_play_dir)
    else:
        team_dir = s_play_dir

    s_motion_dir, i_motion_dir, dir_offset = get_general_direction_and_offset(vector_x, vector_y, s_play_dir)
    motion_dir_rel_to_scrimmage = get_motion_dir_relative_to_scrimmage(vector_x, team_dir)

    if abs(dir_offset) > 45:
        print(f"WARN: {name:17} ({player_id}): {f_start:3} - {f_end:3}; {motion_dir:6} {dir_offset}")

    total_distance = round(math.sqrt((vector_x ** 2) + (vector_y ** 2)), 4)
    abs_speed = round(total_distance / motion_time, 4)

    return [ f_start, f_end, vector_x, vector_y, final_x, final_y, x_to_los, s_motion_dir, i_motion_dir,
             dir_offset, team_dir, motion_dir_rel_to_scrimmage, abs_vector_x, total_distance,
             abs_speed ]

def get_motion_events( df_f, df_d, df_pp, df_p ):

    game_id = df_d["gameId"].values[0]
    play_id = df_d["playId"].values[0]

    defense_team  = df_d["defensiveTeam"].values[0]
    line_of_scrimmage = df_d["absoluteYardlineNumber"].values[0]

    start_events = [ "line_set", "man_in_motion" ]
    end_events = [ "ball_snap" ]

    presnap_start = get_min_frame_from_events(df_f, start_events)
    presnap_end = get_max_frame_from_events(df_f, end_events)

    df_pre = get_presnap_dataframe(df_f, presnap_start, presnap_end)
    p_ids = get_player_ids(df_pre)

    l_motions = []
    motion_idx = 11

    for p in p_ids:

        # nflId is nan for the football, so we can ignore it for the loop
        if math.isnan(p):
            continue

        row_player_play = df_pp[ df_pp[ "nflId" ] == p ]
        row_player      = df_p[ df_p [ "nflId" ] == p ]

        position = row_player[ "position" ].values[0]
        team = row_player_play[ "teamAbbr" ].values[0]
        is_defense = (defense_team == team)

        player_stats = [ game_id, play_id, p, position, team, is_defense ]

        t_frames = get_motion_event_frames_by_player(df_pre, p)
        for l in range(len(t_frames)):

            l_stats = summarize_motion_event( df_pre, t_frames[l], p, line_of_scrimmage, is_defense )
            l_motions.append( player_stats + [ motion_idx ] + l_stats )

            motion_idx += 1

    columns = [ "gameId", "playId", "nflId", "position", "teamAbbr", "isDefense", "motionEventId",
                "startFrameId", "endFrameId", "vectorX", "vectorY", "finalX", "finalY",
                "finalXtoLos", "motionDir", "motionDirInt", "dirOffest", "teamDir",
                "motionDirRelativeToScrimmage", "absVectorX", "totalDistance", "absSpeed" ]

    return pd.DataFrame( l_motions, columns=columns )


### MAIN ###

if (len(sys.argv) < 2):
    print("Specify gameId and playId")
    sys.exit(1)

try:
    g_id = sys.argv[1]
except:
    print("Invalid game id format")
    sys.exit(1)

p_id = ""
try:
    p_id = int(sys.argv[2])
except:
    print(f"WARN: No play specified, pulling all plays for game(s): {g_id}")

game_list = g_id.split(",")

df_out = pd.DataFrame([])

plays_file       = ap.DATA_DIR + "/plays.csv"
players_file     = ap.DATA_DIR + "/players.csv"
player_play_file = ap.DATA_DIR + "/player_play.csv"

df_plays       = pd.read_csv(plays_file)
df_players     = pd.read_csv(players_file)
df_player_play = pd.read_csv(player_play_file)

for g in game_list:

    tracking_file  = ap.get_tracking_file_for_week( int(g) )
    df_tracking    = pd.read_csv(tracking_file)

    df_game_frames = ap.filter_frames_by_game( df_tracking, int(g) )
    df_game_plays  = ap.filter_frames_by_game( df_plays, int(g) )
    df_game_pp     = ap.filter_frames_by_game( df_player_play, int(g) )

    if p_id:
        list_plays = [ p_id ]
    else:
        list_plays = df_game_plays["playId"].unique()

    count = 0

    print(f"Progress ({g}): ", end='', flush=True)

    for p in list_plays:

        # the for loop is slow, print a progress bar; maybe we can use a group_by
        # here instead?
        count += 1
        if (count % 10) == 0:
            print('.', end='', flush=True)

        df_play_tracking_frames = ap.filter_frames_by_play( df_game_frames, p )
        df_play_details         = ap.filter_frames_by_play( df_game_plays, p)
        df_players_plays        = ap.filter_frames_by_play( df_game_pp, p )

        df_motion_events = get_motion_events( df_play_tracking_frames, df_play_details,
                                              df_players_plays, df_players )

        df_out = pd.concat( [ df_out, df_motion_events ] )

    print()

s_game_id = ""
if len(game_list) == 1:
    s_game_id = game_list[0]

outfile = get_motion_event_filename(s_game_id)

print(f"DataFrame (shape: {df_out.shape}) to file {outfile}")
df_out.to_csv(f"data/processed/{outfile}", index=False)
