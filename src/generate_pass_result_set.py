import pandas as pd
import math
import sys

def is_passer(df_pp_row):
    return ( df_pp_row["passingYards"]  > 0 )

def is_receiver(df_pp_row):
    return( df_pp_row["hadPassReception"] > 0 )

# load game data, get array of games in week 1
df_gs = pd.read_csv("data/kaggle/games.csv")
df_gs_week1 = df_gs[ df_gs["week"] == 1 ]

list_games_week1 = df_gs_week1[ "gameId" ].unique()
#print(list_games_week1)

# load player play data
df_pp = pd.read_csv("data/kaggle/player_play.csv")

# limit player play data to week 1
df_pp_week1 = df_pp[ df_pp["gameId"].isin(list_games_week1) ].copy()

# create is_passer and is_receiver columns by applying function
df_pp_week1["isPasser"] = df_pp_week1.apply(is_passer, axis=1)
df_pp_week1["isReceiver"] = df_pp_week1.apply(is_receiver, axis=1)

# write result set to csv
header = [ "gameId", "playId", "nflId", "isPasser", "isReceiver" ]
df_pp_week1.to_csv('data/pass_result_set.csv', columns=header, index=False)
