# script and library to analyze plays

import pandas as pd
import numpy as np
import math

import scipy.stats as st
import scipy.spatial as sp

#from scipy.spatial import distance

import sys

### CONSTANTS ###

RAW_DATA_DIR = "data/kaggle"
PROCESSED_DATA_DIR = "data/processed"

#DATA_DIR = "/kaggle/input/nfl-big-data-bowl-2025"
#DATA_DIR = 'data/kaggle'

### FUNCTIONS ###

def get_defensive_players_in_game_by_team( game_id, team ):

    l_defensive_players = []

    df_play = pd.read_csv(f"{RAW_DATA_DIR}/plays.csv")
    df_player_play = pd.read_csv(f"{RAW_DATA_DIR}/player_play.csv")

    # find all plays where team was on defense
    df_defensive_plays = df_play[ ( df_play[ "gameId" ] == int(game_id) ) & \
                                  ( df_play[ "defensiveTeam" ] == team ) ]
    l_def_plays = df_defensive_plays[ "playId" ].unique()

    # get all players from team's defensive plays
    df_players = df_player_play[ ( df_player_play[ "gameId" ] == int(game_id) ) & \
                                 ( df_player_play[ "teamAbbr" ] == team ) & \
                                 ( df_player_play[ "playId" ].isin(l_def_plays) ) ]
    l_defensive_players = df_players[ "nflId" ].unique()

    return l_defensive_players

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

def get_tracking_file_for_week( game_id ):

    tracking_prefix = RAW_DATA_DIR + "/tracking_week_"
    games_file = RAW_DATA_DIR + "/games.csv"
    df_game = pd.read_csv( games_file )

    try:
        week_number = df_game[(df_game["gameId"] == game_id)]["week"].values[0]
    except:
        print("Could not find week for game")
        sys.exit(1)

    return tracking_prefix + str(week_number) + ".csv"

def filter_frames_by_game( df_tr, game_id ):

    df_frames = df_tr[
        (df_tr["gameId"] == game_id)
    ].copy()

    return df_frames

def filter_frames_by_play( df_tr, play_id ):

    df_frames = df_tr[
        (df_tr["playId"] == play_id)
    ].copy()

    return df_frames

def load_tracking_from_game_and_play( game_id, play_id ):

    tracking_file = get_tracking_file_for_week( game_id )
    plays_file = RAW_DATA_DIR + "/plays.csv"

    df_plays = pd.read_csv(plays_file)
    df_tracking = pd.read_csv(tracking_file)

    df_game_frames = filter_frames_by_game( df_tracking, game_id )
    df_play_frames = filter_frames_by_play( df_game_frames, play_id )

    df_details = df_plays[
        (df_plays["playId"] == play_id) & \
        (df_plays["gameId"] == game_id)
    ]

    return df_play_frames, df_details

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

def get_pre_snap_frames(df):
    pass

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

    dist = sp.distance.euclidean((p1_x, p1_y), (p2_x, p2_y))
    return dist

def get_closest_player_to_point(x, y, df_players):

    min_distance = 200
    min_player_id = 0

    for i, p in df_players.iterrows():
        dist = sp.distance.euclidean((x, y),(p["x"], p["y"]))
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
        dist = sp.distance.euclidean((o_x, o_y),(p["x"], p["y"]))
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
    min_player, min_distance = get_closest_player_to_point(f_x, f_y, player_rows)

    return min_player

def find_targeted_receiver_id(p_df, d_df):

    t_x = d_df["targetX"].values[0]
    t_y = d_df["targetY"].values[0]

    min_player = 0
    if not (math.isnan(t_x) or math.isnan(t_y)):
        min_player, min_distance = get_closest_player_to_point(t_x, t_y, p_df)

    return min_player

def print_pre_snap_analysis(df, club, is_offense):

    if is_offense:
        print(f"  Offense: {club}")
    else:
        print(f"  Defense: {club}")

    team_pre_snap = df[ df[ "club" ] == club ]
    spd, p_id, f_id = get_top_speed_from_player_frames(team_pre_snap)
    name = get_player_name_by_id( df, p_id )

    print(f"    Top speed: {name}, {spd} yd/s at frame {f_id}")

    distance_traveled = get_distance_traveled_from_player_frames(team_pre_snap)

    print(f"    Team moved {distance_traveled} yds total before the snap")

    return True

def calc_team_dist(df_players):

    df_players_pos = df_players[[ "x", "y" ]]
    mean = np.mean(df_players_pos, axis=0)
    cov = np.cov(df_players_pos, rowvar=False)

    return mean, cov

def score_z_values(X, Y, mean, cov, weight=1):

    pos = np.dstack((X, Y))
    rv = st.multivariate_normal(mean, cov)

    Z_pre = rv.pdf(pos)
    Z = [ (weight * x) for x in Z_pre ]

    Z_mean = rv.pdf(mean) * weight

    return Z

def generate_mesh_grid(max_x, min_x, max_y, min_y):

    range_x = np.linspace(min_x, max_x)
    range_y = np.linspace(min_y, max_y)

    X, Y = np.meshgrid(range_x, range_y)

    return X, Y

def print_distribution_details( mean, cov ):

    x = round(mean[0], 2)
    y = round(mean[1], 2)

    print( f"  mean: {x}, {y}" )
    print( f"  cov: {cov[0]} {cov[1]}")

    return True


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

    df_tracking_unmerged, df_play_details = load_tracking_from_game_and_play(
        game_id, play_id)
    df_tracking_unmerged[[ "nflId" ]] = df_tracking_unmerged[[ "nflId" ]].fillna(-1)

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
    df_tr = df_tracking_unmerged.merge(df_player_positions, on=['nflId'])

    # print events log
    df_events = df_tr[[ "frameId", "event" ]].dropna()
    df_events = df_events.drop_duplicates()

    print(df_events.to_string(index=False))
    print()

    print(f"{df_play_details['playDescription'].values[0]}")
    print()

    print("Play details")
    expected_points = round(df_play_details['expectedPoints'].values[0],2)
    print(f"  Expected Points:       {expected_points}")
    points_added = round(df_play_details['expectedPointsAdded'].values[0],2)
    print(f"  Expected Points Added: {points_added}")
    offense_formation = df_play_details['offenseFormation'].values[0]
    print(f"  Offense Formation:     {offense_formation}")
    receiver_alignment = df_play_details['receiverAlignment'].values[0]
    print(f"  Receiver Alignment:    {receiver_alignment}")
    pass_coverage = df_play_details['pff_passCoverage'].values[0]
    print(f"  Pass Coverage:         {pass_coverage}")
    print()

    is_pass_play = False
    is_run_play  = False

    # is this play a run, pass or other?

    snap_frame_id = get_frame_id_for_event(df_tr, "ball_snap")

    pass_forward_frame_id = get_frame_id_for_event(df_tr, "pass_forward")
    pass_shovel_frame_id = get_frame_id_for_event(df_tr, "pass_shovel")
    handoff_frame_id = get_frame_id_for_event(df_tr, "handoff")
    run_frame_id = get_frame_id_for_event(df_tr, "run")
    sack_frame_id = get_frame_id_for_event(df_tr, "qb_sack")

    # check if this is a pass play
    if (handoff_frame_id > 0):
        is_run_play = True
        frame_id = handoff_frame_id
    elif (run_frame_id > 0):
        is_run_play = True
        frame_id = run_frame_id
    elif (pass_forward_frame_id > 0):
        is_pass_play = True
        frame_id = pass_forward_frame_id
    elif (pass_shovel_frame_id > 0):
        is_pass_play = True
        frame_id = pass_shovel_frame_id
    elif (sack_frame_id > 0):
        frame_id = sack_frame_id

    df_frame = df_tr[ df_tr["frameId"] == frame_id ]

    # we can't assumes that there's only 1 quarterback on the play; see play
    # game_id: 2022091100, play_id: 2114 for an example where there are two
    # quarterbacks on the field (Taysom Hill and Jameis Winston)

    # has the football 1 second after the snap
    after_snap_frame_id = snap_frame_id + 10
    passer_id = find_player_id_by_closest_to_football( df_tr, after_snap_frame_id )
    ballcarrier_id = 0

    # if it's a pass play, find the nearest reciever; if it's a run play
    # find the player nearest to the ball 0.5 seconds after hand off
    if is_pass_play:
        ballcarrier_id = find_targeted_receiver_id( df_tr, df_play_details )
    elif is_run_play:
        ballcarrier_id = find_player_id_by_closest_to_football( df_tr, frame_id+5 )

    passer_name = get_player_name_by_id( df_players, passer_id )
    if ballcarrier_id != 0:
        ballcarrier_name = get_player_name_by_id( df_players, ballcarrier_id )
    else:
        ballcarrier_name = "no receiver"

    events = []
    if is_pass_play:
        events = [ "pass_forward", "pass_arrived" ]
    elif is_run_play:
        events = [ "handoff", "run", "tackle" ]

    print(f"Pre-snap analysis")

    set_frame_id = get_frame_id_for_event(df_events, "line_set")
    snap_frame_id = get_frame_id_for_event(df_events, "ball_snap")

    offense_team = df_play_details[ "possessionTeam" ].values[0]
    defense_team = df_play_details[ "defensiveTeam" ].values[0]

    # pull offense team distribution at set
    df_offense_at_set = df_tr[ ( df_tr[ "frameId" ] == set_frame_id ) & \
                               ( df_tr[ "club" ] == offense_team )
                             ]
    off_mean_at_set, off_cov_at_set = calc_team_dist(df_offense_at_set)

    # pull offense team distribution as snap
    df_offense_at_snap = df_tr[ ( df_tr[ "frameId" ] == snap_frame_id ) & \
                                ( df_tr[ "club" ] == offense_team )
                              ]
    off_mean_at_snap, off_cov_at_snap = calc_team_dist(df_offense_at_snap)

    #off_dist_at_set = st.multivariate_normal(off_mean_at_set, off_cov_at_set)
    #off_dist_at_snap = st.multivariate_normal(off_mean_at_snap, off_cov_at_snap)
    #print(off_dist_at_set.entropy())
    #print(off_dist_at_snap.entropy())

    # compare distributions
    #print(off_cov_at_set)
    #print(off_cov_at_snap)


    # build a dataframe of pre-snap frames
    df_pre_snap = df_tr[ ( df_tr[ "frameId" ] >= set_frame_id ) & \
                         ( df_tr[ "frameId" ] <= snap_frame_id )
                       ]

    print_pre_snap_analysis( df_pre_snap, offense_team, True)
    print_pre_snap_analysis( df_pre_snap, defense_team, False )
    print()

    for e in events:

        frame_id = get_frame_id_for_event(df_events, e)
        f = df_tr[ df_tr["frameId"] == frame_id ]

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
