import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import analyze_play as ap

import glob
import sys

#ap.DATA_DIR = 'data/kaggle'

def get_player_column(df, player_id, col_name):

    df_p = df[ df[ "nflId" ] == player_id ].copy()
    name = df_p[ "displayName" ].iloc[0]

    df_p = df_p[[ "frameId", col_name ]]
    df_p = df_p.rename(columns={col_name: name})

    return df_p

def get_player_list_sorted_by_speed(df):

    player_speeds = df.groupby('nflId')['s'].sum()
    player_speeds.sort_values(ascending=False, inplace=True)

    return player_speeds.index

def build_player_columns(df_f, df_m, col_name, p_list):

    # initiate dataframe for plot
    df_players = pd.DataFrame([])
    hash_colors = {}

    highlight_color = [ '#880000', '#008800', '#000088' ]
    default_color = '#DDDDDD'

    highlight_index = 0
    for p in p_list:

        df_p_col = get_player_column( df_f, p, col_name )

        if not df_players.empty:
            df_players = df_players.merge(df_p_col, on=['frameId'])
        else:
            df_players = df_p_col

        df_m_player = df_m[ df_m[ "nflId" ] == p ]
        #print(p)

        if df_m_player.empty:
            hash_colors[df_p_col.columns[1]] = default_color
        else:
            hash_colors[df_p_col.columns[1]] = highlight_color[ highlight_index ]
            highlight_index += 1

    df_players.set_index('frameId', inplace=True)

    return df_players, hash_colors

def build_team_columns(df_f, df_m, team, column_name):

    # get list of unique team player id's in frame
    df_ = df_f[ df_f[ "club" ] == team ]
    p_ids = get_player_list_sorted_by_speed(df_)
    df_team, hash_colors = build_player_columns( df_, df_m, column_name, p_ids )

    return df_team, hash_colors

def set_subplot_details(ax, df, title, colors, set_f_id, snap_f_id, motion_f_id=0, shift_f_id=0):

    df.plot.line(ax=ax, color=colors)

    ax.set_title(title)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    ax.set_xlabel("Frame")
    ax.set_ylabel("Speed")

    ax.axvline(x=set_f_id, color='red', linestyle='--', label="Line Set")
    ax.axvline(x=snap_f_id, color='green', linestyle='--', label="Snap")

    if motion_f_id > 0:
        ax.axvline(x=motion_f_id, color='gray', linestyle=':', label="Man in Motion")
    if shift_f_id > 0:
        ax.axvline(x=shift_f_id, color='gray', linestyle=':', label="Shift")

    return True

def set_fill_between(ax, df_f, df_m):

    for i, m in df_m.iterrows():

        name = m["displayName"]
        start = m["startFrameId"]
        end = m["endFrameId"]

        x = df_f.index.values
        y = df_f[name].values
        ax.fill_between(x, y, where=((x>start) & (x<end)), color="#DDDDDD",
                        alpha=0.5)

    return True

def summarize_speed_over_time(df_team):

    list_summary = []
    index = df_team.index

    for col_name, column in df_team.items():

        row = { 'name': col_name,
                'max_spd': column.max(),
                'sum_spd': column.sum()
              }
        list_summary.append(row)

    df_summary = pd.DataFrame(list_summary)
    df_summary.sort_values(by="sum_spd", inplace=True, ascending=False)
    print(df_summary.to_string(index=False))

def plot_player_speed_over_time(game_id, play_id, player_list):

    df_f, df_d = ap.load_tracking_from_game_and_play(game_id, play_id)

    set_frame_id = ap.get_frame_id_for_event(df_f, "line_set")
    snap_frame_id = ap.get_frame_id_for_event(df_f, "ball_snap")

    df_presnap = df_f[ ( df_f[ "frameId" ] >= set_frame_id ) & \
                       ( df_f[ "frameId" ] <= snap_frame_id) & \
                       ( df_f[ "nflId" ].isin( player_list ) )
                     ]

    df_players = build_player_columns(df_presnap, "s", player_list)
    df_players.plot.line()

    plt.xlabel("Frame")
    plt.ylabel("Speed")
    plt.show()

    return df_d[ "playDescription" ].values[0]


def plot_speed_over_time( game_id, play_id ):

    df_f, df_d = ap.load_tracking_from_game_and_play(game_id, play_id)

    motion_filename  = f"{ap.PROCESSED_DATA_DIR}/motion.2022091102.20250105.18*"
    players_filename = f"{ap.RAW_DATA_DIR}/players.csv"

    motion_files_found = glob.glob(motion_filename)
    if len(motion_files_found) > 1:
        print(f"ERROR: Motion file {motion_filename} is not specific enough; " \
              f"found {len(motion_files_found)} files")
        sys.exit(1)

    df_players = pd.read_csv(players_filename)
    df_motion = pd.read_csv(motion_files_found[0])

    df_game_motion = ap.filter_frames_by_game( df_motion, game_id )
    df_play_motion = ap.filter_frames_by_play( df_game_motion, play_id )

    df_player_subset = df_players[[ "nflId", "displayName" ]]
    df_motion_merged = df_play_motion.merge( df_player_subset, on=[ "nflId" ] )

    offense_team = df_d[ "possessionTeam" ].values[0]
    defense_team = df_d[ "defensiveTeam" ].values[0]

    start_events = [ "line_set", "man_in_motion" ]
    end_events = [ "ball_snap" ]

    presnap_start = ap.get_min_frame_from_events(df_f, start_events)
    presnap_end = ap.get_max_frame_from_events(df_f, end_events)

    frame_padding = 7
    df_pre = ap.get_presnap_dataframe( df_f, presnap_start, presnap_end, frame_padding )

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10,8))

    column = "s"
    df_offense, off_color = build_team_columns(df_pre, df_motion_merged, offense_team, column)
    set_subplot_details(axes[0], df_offense, f"Offense: {offense_team}", off_color,
                        presnap_start, presnap_end)

    df_offense_motion = df_motion_merged [ df_motion_merged[ "teamAbbr" ] == offense_team ]
    set_fill_between(axes[0], df_offense, df_offense_motion)

    df_defense, def_color = build_team_columns(df_pre, df_motion_merged, defense_team, column)
    set_subplot_details(axes[1], df_defense, f"Defense: {defense_team}", def_color,
                        presnap_start, presnap_end)

    df_defense_motion = df_motion_merged [ df_motion_merged[ "teamAbbr" ] == defense_team ]
    set_fill_between(axes[1], df_defense, df_defense_motion)

    #print("Offense:")
    #summarize_speed_over_time(df_offense)
    #print("\nDefense:")
    #summarize_speed_over_time(df_defense)

    plt.tight_layout()
    plt.show()

    return df_d[ "playDescription" ].values[0]

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

    try:
        players_list = sys.argv[3].split(",")
    except:
        players_list = []

    players = list(map(int, players_list))
    if not players:
        details = plot_speed_over_time(game_id, play_id)
    else:
        details = plot_player_speed_over_time(game_id, play_id, players)

    print(details)
