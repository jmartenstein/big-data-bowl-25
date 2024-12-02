import matplotlib.pyplot as plt
import analyze_play as ap
import pandas as pd
import numpy as np

# get array of games in week 1
df_gs = pd.read_csv("data/kaggle/games.csv")
df_gs_week1 = df_gs[ df_gs["week"] == 1 ]
list_games_week1 = df_gs_week1[ "gameId" ].unique()

# load player play data for week1
df_ps = pd.read_csv("data/kaggle/plays.csv")
df_ps_week1 = df_ps[ ( df_ps["gameId"].isin(list_games_week1) ) ].copy()

print(df_ps_week1.shape)

# load player play data, limit to week 1
df_tr = pd.read_csv("data/kaggle/tracking_week_1.csv")
df_tr_week1 = df_tr[ df_tr["gameId"].isin(list_games_week1) ]

count = 0

# can this be replaced with an group_by / reduce?
for idx, row in df_ps_week1.iterrows():

    game_id = row[ "gameId" ]
    play_id = row[ "playId" ]

    offense = row[ "possessionTeam" ]
    defense = row[ "defensiveTeam" ]

    df_play_tr = df_tr_week1[ ( df_tr_week1[ "gameId" ] == game_id ) & \
                              ( df_tr_week1[ "playId" ] == play_id )
                            ]

    set_frame_id = ap.get_frame_id_for_event(df_play_tr, "line_set")
    snap_frame_id = ap.get_frame_id_for_event(df_play_tr, "ball_snap")

    df_pre_snap = df_play_tr[ ( df_play_tr[ "frameId" ] >= set_frame_id ) & \
                              ( df_play_tr[ "frameId" ] <= snap_frame_id )
                            ]

    df_offense_pre_snap = df_pre_snap[ df_pre_snap[ "club" ] == offense ]
    offense_dist = ap.get_distance_traveled_from_player_frames(df_offense_pre_snap)
    df_ps_week1.loc[ idx, "offenseDistanceTraveled" ] = offense_dist

    df_defense_pre_snap = df_pre_snap[ df_pre_snap[ "club" ] == defense ]
    defense_dist = ap.get_distance_traveled_from_player_frames(df_defense_pre_snap)
    df_ps_week1.loc[ idx, "defenseDistanceTraveled" ] = defense_dist

    # the for loop is slow, print a progress bar; maybe we can use a group_by
    # here instead?
    count += 1
    if (count % 100) == 0:
        print('.', end='', flush=True)

print()
print(df_ps_week1)

data = df_ps_week1[[ "offenseDistanceTraveled" ]]
num_bins = 50

hist, bin_edges = np.histogram(data, num_bins)
plt.hist(data, num_bins)
plt.xlim(0,40)

plt.show()


