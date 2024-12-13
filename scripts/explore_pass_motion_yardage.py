import pandas as pd
import sys

# load game data, get array of games in week 1
df_gs = pd.read_csv("data/kaggle/games.csv")
df_gs_week1 = df_gs[ df_gs["week"] == 1 ]

list_games_week1 = df_gs_week1[ "gameId" ].unique()

# load player play data, limit to week 1
df_pp = pd.read_csv("data/kaggle/player_play.csv")
df_pp_week1 = df_pp[ df_pp["gameId"].isin(list_games_week1) ]

# get plays with motion and yards after catch
df_yardage_gained = df_pp_week1[ df_pp_week1[ "yardageGainedAfterTheCatch" ] > 10 & \
                                 df_pp_week1[ "motionSinceLineset" ] ].copy()
df_yg_sorted = df_yardage_gained.sort_values(by="yardageGainedAfterTheCatch",
                                             ascending=False)
df_top = df_yg_sorted[:10]
print(df_top[[ "gameId", "playId", "nflId", "yardageGainedAfterTheCatch" ]])
print()

# get plays with motion, between 10 and 20 yards target past the line
# of scrimmage and incomplete
df_incomplete = df_pp_week1[ ( df_pp_week1[ "wasTargettedReceiver" ] > 0 ) & \
                             ( df_pp_week1[ "motionSinceLineset" ] == True ) & \
                             ( df_pp_week1[ "hadPassReception" ] == 0 ) ].copy()
#df_incomplete_sorted = df_incomplete,sort_values(by="passLength", ascending=False)
df_incomplete_top = df_incomplete[:10]
print(df_incomplete_top[[ "gameId", "playId", "nflId", "wasTargettedReceiver"]])
