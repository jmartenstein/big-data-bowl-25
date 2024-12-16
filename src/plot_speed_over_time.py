import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import analyze_play as ap
import sys

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

def build_team_columns(df, team, column_name):

    # initiate dataframe for plot
    df_team = pd.DataFrame([])

    # get list of unique team player id's in frame
    df_ = df[ df[ "club" ] == team ]
    p_ids = get_player_list_sorted_by_speed(df_)

    for p in p_ids:

        df_p_spd = get_player_column( df_, p, column_name )

        if not df_team.empty:
            df_team = df_team.merge(df_p_spd, on=['frameId'])
        else:
            df_team = df_p_spd

    df_team.set_index('frameId', inplace=True)

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

def summarize_player_stats(df_team):

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

    details = plot_speed_over_time(game_id, play_id)
    print(details)
