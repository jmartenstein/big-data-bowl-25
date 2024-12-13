import matplotlib.pyplot as plt
import pandas as pd

import sys

# get array of games in week 1
df_gs = pd.read_csv("data/kaggle/games.csv")
df_gs_week1 = df_gs[ df_gs["week"] == 1 ]
list_games_week1 = df_gs_week1[ "gameId" ].unique()

# load player play data for week1
df_ps = pd.read_csv("data/kaggle/plays.csv")
df_ps_week1 = df_ps[ ( df_ps["gameId"].isin(list_games_week1) ) ]

# remove incomplete passes
df_ps_week1 = df_ps_week1[ df_ps_week1[ "passResult" ] != "I" ]

print(df_ps_week1.shape)

yards = df_ps_week1["prePenaltyYardsGained"].values
epa =   df_ps_week1["expectedPointsAdded"].values
drop = df_ps_week1["isDropback"].values

fig, ax = plt.subplots()
scatter = ax.scatter( epa, yards, c=drop)
ax.set_xlabel("EPA")
ax.set_ylabel("Yards Gained")

set_limits = True
#set_limits = False
if set_limits:
    ax.set_xlim(-3, 3)
    ax.set_ylim(-10, 20)

handles, labels = scatter.legend_elements()
labels = ["False", "True"]
ax.legend(handles, labels, title="Pass Attempt")

plt.show()

