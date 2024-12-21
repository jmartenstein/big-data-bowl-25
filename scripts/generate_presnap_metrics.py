import matplotlib.pyplot as plt
import analyze_play as ap
import pandas as pd
import numpy as np

import sys

### FUNCTIONS

def get_max_team_speed_per_play(df, game_id, player_id, s_team):

    # get max speed for this play
    max_row = df[
        ( df['gameId'] == game_id ) & \
        ( df['playId'] == play_id ) & \
        ( df['club'] == s_team )
    ]
    if len(max_row) > 0:
        max_speed = max_row['s'].values[0]
    else:
        print(f"WARN: No max speed found for {game_id}, {play_id}, {s_team}")
        max_speed = 0

    return max_speed

start_week = 1
end_week = 6

df_all_weeks = pd.DataFrame([])

for w in range(start_week, end_week+1):

    print(f"Analyzing Week {w}")

    # get array of games in week 1
    df_gs = pd.read_csv("data/kaggle/games.csv")
    df_gs_weeks = df_gs[ df_gs["week"] == w ]
    list_games_weeks = df_gs_weeks[ "gameId" ].unique()

    # load player play data for week1
    df_ps = pd.read_csv("data/kaggle/plays.csv")
    df_ps_weeks = df_ps[ ( df_ps["gameId"].isin(list_games_weeks) ) ].copy()

    # load player play data, limit to week 1
    df_tr = pd.read_csv(f"data/kaggle/tracking_week_{w}.csv")
    df_tr_weeks = df_tr[ df_tr["gameId"].isin(list_games_weeks) ]

    # run group by to find max speed for each team per play
    df_max_speed = df_tr_weeks.groupby(['gameId', 'playId', 'club'],
                                       as_index = False)[['s']].max()

    count = 0
    print(f"Plays: {len(df_ps_weeks)}")
    print(f"Speed summary: {df_max_speed.shape}")

    # can this be replaced with an group_by / reduce?
    for idx, row in df_ps_weeks.iterrows():

        game_id = row[ "gameId" ]
        play_id = row[ "playId" ]

        offense = row[ "possessionTeam" ]
        defense = row[ "defensiveTeam" ]

        max_offense_speed = get_max_team_speed_per_play(
            df_max_speed, game_id, play_id, offense)
        df_ps_weeks.loc[ idx, "maxOffenseSpeed" ] = max_offense_speed

        max_defense_speed = get_max_team_speed_per_play(
            df_max_speed, game_id, play_id, defense)
        df_ps_weeks.loc[ idx, "maxDefenseSpeed" ] = max_defense_speed

        df_play_tr = df_tr_weeks[ ( df_tr_weeks[ "gameId" ] == game_id ) & \
                                  ( df_tr_weeks[ "playId" ] == play_id )
                                ]

        set_frame_id = ap.get_frame_id_for_event(df_play_tr, "line_set")
        snap_frame_id = ap.get_frame_id_for_event(df_play_tr, "ball_snap")

        df_pre_snap = df_play_tr[ ( df_play_tr[ "frameId" ] >= set_frame_id ) & \
                                  ( df_play_tr[ "frameId" ] <= snap_frame_id )
                                ]

        df_offense_pre_snap = df_pre_snap[ df_pre_snap[ "club" ] == offense ]
        offense_dist = ap.get_distance_traveled_from_player_frames(df_offense_pre_snap)
        df_ps_weeks.loc[ idx, "offenseDistanceTraveled" ] = offense_dist

        df_defense_pre_snap = df_pre_snap[ df_pre_snap[ "club" ] == defense ]
        defense_dist = ap.get_distance_traveled_from_player_frames(df_defense_pre_snap)
        df_ps_weeks.loc[ idx, "defenseDistanceTraveled" ] = defense_dist

        df_ps_weeks.loc[ idx, "elapsedTime" ] = (snap_frame_id - set_frame_id) / 10

        # the for loop is slow, print a progress bar; maybe we can use a group_by
        # here instead?
        count += 1
        if (count % 100) == 0:
            print('.', end='', flush=True)

    print()

    output_features = [ "gameId",
                        "playId",
                        "passLength",
                        "passResult",
                        "penaltyYards",
                        "yardsGained",
                        "yardsToGo",
                        "maxOffenseSpeed",
                        "maxDefenseSpeed",
                        "offenseDistanceTraveled",
                        "defenseDistanceTraveled",
                        "elapsedTime" ]

    df_all_weeks = pd.concat( [ df_all_weeks, df_ps_weeks ] )

df_all_weeks[ output_features ].to_csv('data/processed/plays_presnap_summary.csv', index=False)
