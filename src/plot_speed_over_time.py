import matplotlib.pyplot as plt
import pandas as pd
import analyze_play as ap
import sys

def get_player_speed_frame(df, player_id):

    df_p = df[ df[ "nflId" ] == player_id ].copy()
    name = df_p[ "displayName" ].iloc[0]

    df_p = df_p[[ "frameId", "s" ]]
    df_p = df_p.rename(columns={'s': name})

    return df_p

def build_team_columns(df, team):

    # initiate dataframe for plot
    df_team = pd.DataFrame([])

    # get list of unique team player id's in frame
    df_ = df[ df[ "club" ] == team ]
    p_ids = df_[ "nflId" ].unique()

    for p in p_ids:

        df_p_spd = get_player_speed_frame( df_presnap_frames, p )

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


    data_dir = "./data/kaggle"

    tracking_prefix = data_dir + "/tracking_week_"
    plays_file = data_dir + "/plays.csv"
    games_file = data_dir + "/games.csv"

    df_game = pd.read_csv(games_file)

    try:
        week_number = df_game[(df_game["gameId"] == game_id)]["week"].values[0]
    except:
        print("Could not find week for game")
        sys.exit(1)

    tracking_file = tracking_prefix + str(week_number) + ".csv"
    df_tr = pd.read_csv(tracking_file)
    df_ps = pd.read_csv(plays_file)

    df_frames = df_tr[
        (df_tr["playId"] == play_id) & \
        (df_tr["gameId"] == game_id)
    ].copy()

    df_details = df_ps[
        (df_ps["playId"] == play_id) & \
        (df_ps["gameId"] == game_id)
    ]

    offense_team = df_details[ "possessionTeam" ].values[0]
    defense_team = df_details[ "defensiveTeam" ].values[0]

    print(df_details[ "playDescription" ].values[0])

    set_frame_id = ap.get_frame_id_for_event(df_frames, "line_set")
    snap_frame_id = ap.get_frame_id_for_event(df_frames, "ball_snap")
    motion_frame_id = ap.get_frame_id_for_event(df_frames, "man_in_motion")
    shift_frame_id = ap.get_frame_id_for_event(df_frames, "shift")

    frame_padding = 7
    df_presnap_frames = df_frames[ ( df_frames[ "frameId" ] >= set_frame_id - frame_padding ) & \
                                   ( df_frames[ "frameId" ] <= snap_frame_id + frame_padding )
                                 ]

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10,8))

    df_offense = build_team_columns(df_presnap_frames, offense_team)
    set_subplot_details(axes[0], df_offense, f"Offense: {offense_team}",
                        set_frame_id, snap_frame_id, motion_frame_id, shift_frame_id)

    df_defense = build_team_columns(df_presnap_frames, defense_team)
    set_subplot_details(axes[1], df_defense, f"Defense: {defense_team}",
                        set_frame_id, snap_frame_id, motion_frame_id, shift_frame_id)

    plt.tight_layout()
    plt.show()
