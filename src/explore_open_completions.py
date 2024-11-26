import pandas as pd
import sys

import analyze_play as ap

def get_distance_from_scrimmage(df_row):

    x = df_row[ "targetX" ]
    yardline = df_row[ "absoluteYardlineNumber"  ]

    return round(abs( yardline - x), 2)

# load game data, get array of games in week 1
df_gs = pd.read_csv("data/kaggle/games.csv")
df_gs_week1 = df_gs[ df_gs["week"] == 1 ]

# get list of unique games
list_games_week1 = df_gs_week1[ "gameId" ].unique()

# load player play data, limit to week 1
df_tr = pd.read_csv("data/kaggle/tracking_week_1.csv")
df_tr_week1 = df_tr[ df_tr["gameId"].isin(list_games_week1) ]

# load plays result data, limit to week 1
df_ps = pd.read_csv("data/kaggle/plays.csv")
df_ps_week1 = df_ps[ df_ps["gameId"].isin(list_games_week1) ].copy()

#print(df_ps_week1.shape)

#df_cp_week1 = df_ps_week1[ df_ps_week1["passResult"] == "C" ]

#df_ps_week1_first10 = df_ps_week1[:20]
df_ps_week1["catchDistanceFromScrimmage"] = df_ps_week1.apply(
    get_distance_from_scrimmage, axis=1)

df_ps_subset = df_ps_week1[[ "gameId", "playId", "possessionTeam", "targetX",
                             "targetY", "passResult", "catchDistanceFromScrimmage" ]]

df_merge = df_tr_week1.merge(df_ps_subset, on=['gameId','playId'])

distance_threshold = 15
df_deep = df_merge[ ( df_merge[ 'passResult' ] == 'I' ) & \
                    ( df_merge[ 'event' ] == 'pass_forward' ) & \
                    ( df_merge[ 'catchDistanceFromScrimmage' ] > distance_threshold ) ]

play_count = int(len(df_deep) / 23)
print(f"Found {play_count} plays with complete passes at greater than "
      f"{distance_threshold} yards from scrimmage")

df_pass_results = []

for g in list_games_week1:

    # get unique frames / passes
    df_game_plays = df_deep[ df_deep[ "gameId" ] == g ]
    list_unique_plays = df_game_plays[ "playId" ].unique()

    for p in list_unique_plays:

        # get frame data for this play
        df_frame_play = df_game_plays[ df_game_plays[ "playId" ] == p ]

        # pull summary data off of the football row
        df_football_row = df_frame_play[ df_frame_play[ "club" ] == "football" ]
        target_x = df_football_row["x"].values[0]
        target_y = df_football_row["y"].values[0]
        offense = df_football_row["possessionTeam"].values[0]
        result = df_football_row["passResult"].values[0]

        # get frames for offense players
        df_offense = df_frame_play[ df_frame_play[ "club" ] == offense ]

        # find the receiver (closest to target)
        closest_offense, distance = ap.get_closest_player_to_point(target_x,
                                                                   target_y,
                                                                   df_offense)
        # find the nearest defender to player
        closest_defense, player_distance = ap.get_closest_defender(df_frame_play,
                                                                   closest_offense)

        # add results to pass results data frame

        # print play information
        print(f"{g}, {p} - offense: {closest_offense}, defense: {closest_defense}, "
              f"distance: {round(player_distance,2)}, result: {result}")
        #print(closest_defense)
