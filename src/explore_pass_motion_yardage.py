import pandas as pd
import sys

# load game data, get array of games in week 1
df_gs = pd.read_csv("data/kaggle/games.csv")
df_gs_week1 = df_gs[ df_gs["week"] == 1 ]

list_games_week1 = df_gs_week1[ "gameId" ].unique()

# load player play data, limit to week 1
df_pp = pd.read_csv("data/kaggle/player_play.csv")
df_pp_week1 = df_pp[ df_pp["gameId"].isin(list_games_week1) ]

# get plays with motion and top 10 yards after catch
df_yardage_gained = df_pp_week1[ df_pp_week1[ "yardageGainedAfterTheCatch" ] > 0 & \
                                 df_pp_week1[ "motionSinceLineset" ] ].copy()

print(df_yardage_gained.shape)

df_yg_sorted = df_yardage_gained.sort_values(by="yardageGainedAfterTheCatch",
                                             ascending=False)

df_top10 = df_yg_sorted[:5]
print(df_top10[[ "gameId", "playId", "nflId", "yardageGainedAfterTheCatch" ]])





