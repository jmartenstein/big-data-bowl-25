import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import analyze_play as ap
import sys

ap.DATA_DIR = 'data/kaggle'

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

def build_player_columns(df, col_name, p_list):

    # initiate dataframe for plot
    df_players = pd.DataFrame([])

    for p in p_list:

        df_p_col = get_player_column( df, p, col_name )

        if not df_players.empty:
            df_players = df_players.merge(df_p_col, on=['frameId'])
        else:
            df_players = df_p_col

    df_players.set_index('frameId', inplace=True)

    return df_players

def build_team_columns(df, team, column_name):

    # get list of unique team player id's in frame
    df_ = df[ df[ "club" ] == team ]
    p_ids = get_player_list_sorted_by_speed(df_)
    df_team = build_player_columns( df_, column_name, p_ids )

    return df_team

def set_subplot_details(ax, df, title, set_f_id, snap_f_id, motion_f_id, shift_f_id):

    df.plot.line(ax=ax)

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

def plot_speed_over_time(game_id, play_id):

    df_frames, df_details = ap.load_tracking_from_game_and_play(game_id, play_id)

    offense_team = df_details[ "possessionTeam" ].values[0]
    defense_team = df_details[ "defensiveTeam" ].values[0]

    set_frame_id = ap.get_frame_id_for_event(df_frames, "line_set")
    snap_frame_id = ap.get_frame_id_for_event(df_frames, "ball_snap")
    motion_frame_id = ap.get_frame_id_for_event(df_frames, "man_in_motion")
    shift_frame_id = ap.get_frame_id_for_event(df_frames, "shift")

    frame_padding = 7
    df_presnap_frames = df_frames[ ( df_frames[ "frameId" ] >= set_frame_id - frame_padding ) & \
                                   ( df_frames[ "frameId" ] <= snap_frame_id + frame_padding )
                                 ]

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10,8))

    column = "s"
    df_offense = build_team_columns(df_presnap_frames, offense_team, column)
    set_subplot_details(axes[0], df_offense, f"Offense: {offense_team}",
                        set_frame_id, snap_frame_id, motion_frame_id, shift_frame_id)

    df_defense = build_team_columns(df_presnap_frames, defense_team, column)
    set_subplot_details(axes[1], df_defense, f"Defense: {defense_team}",
                        set_frame_id, snap_frame_id, motion_frame_id, shift_frame_id)

    #print("Offense:")
    #summarize_player_stats(df_offense)
    #print("\nDefense:")
    #summarize_player_stats(df_defense)

    plt.tight_layout()
    plt.show()

    return df_details[ "playDescription" ].values[0]

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
