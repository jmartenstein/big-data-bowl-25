import matplotlib.pyplot as plt
import scipy.stats as st
import pandas as pd
import numpy as np
import sys

import analyze_play as ap

def find_frame_boundaries(df_frame, padding, flag_absolute):

    list_x = df_frame["x"].values
    list_y = df_frame["y"].values

    max_x = list_x.max() + padding
    min_x = list_x.min() - padding

    if flag_absolute:
        max_y = 54
        min_y = 0
    else:
        max_y = list_y.max() + padding
        min_y = list_y.min() - padding

    return max_x, min_x, max_y, min_y


def plot_players(plt, df_players):

    df_pos = df_players[[ "x", "y" ]]
    list_x = df_pos["x"].values
    list_y = df_pos["y"].values
    plt.scatter( list_x, list_y )

    return True

def print_point_and_value(x, y, z):

    w = 1/ z
    print(f"  x: {round(x,2)}, y: {round(y,2)}  z: {round(z,2)}, w: {round(w,2)}")
    return True



game_id = 0
play_id = 0
frame_id = 0

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
    sys.exit(1)

try:
    frame_id = int(sys.argv[3])
except:
    print("WARN: No frame specified; setting to snap frame by default")


# load tracking data for the specific frame
df_tr = pd.read_csv("data/kaggle/tracking_week_1.csv")

df_play = df_tr[ ( df_tr[ "gameId" ] ==  game_id ) & \
                  ( df_tr[ "playId" ] ==  play_id )
               ]

# if the frame id isn't set, then pull the snap frame by default
if frame_id == 0:
    frame_id = ap.get_frame_id_for_event(df_play, "ball_snap")
#print(frame_id)

df_frame = df_play[ df_play[ "frameId" ] == frame_id ]

# get offense and defense teams
df_plays = pd.read_csv("data/kaggle/plays.csv")
df_play_details = df_plays[
    (df_plays["playId"] == play_id) & \
    (df_plays["gameId"] == game_id)
]
offense = df_play_details[ "possessionTeam" ].values[0]
defense = df_play_details[ "defensiveTeam" ].values[0]

df_defense_players = df_frame[ df_frame["club"] == defense ]
df_offense_players = df_frame[ df_frame["club"] == offense ]

# plot speed arrows

# plot gaussian influence distributions
def_mean, def_cov = ap.calc_team_dist(df_defense_players)
off_mean, off_cov = ap.calc_team_dist(df_offense_players)

max_x, min_x, max_y, min_y = find_frame_boundaries(df_frame, 5, True)
X, Y = ap.generate_mesh_grid(max_x, min_x, max_y, min_y)

print(f"Defense")
ap.print_distribution_details( def_mean, def_cov )

print(f"Offense")
ap.print_distribution_details( off_mean, off_cov )

def_Z = ap.score_z_values(X, Y, def_mean, def_cov, 100)
off_Z = ap.score_z_values(X, Y, off_mean, off_cov, -100)
Z = [sum(x) for x in zip(def_Z, off_Z)]

# plot players
plt.xlim(min_x, max_x)
plt.ylim(min_y, max_y)
plt.title(f"Players for Frame {frame_id}")

plot_players(plt, df_defense_players)
plot_players(plt, df_offense_players)

plot_mix = True
#plot_mix = False

if plot_mix:
    def_cs = plt.contour( X, Y, Z, levels=6 )
    plt.clabel(def_cs, inline=True, fontsize=6)
else:
    def_cs = plt.contour( X, Y, def_Z, levels=3 )
    plt.clabel(def_cs, inline=True, fontsize=6)
    off_cs = plt.contour( X, Y, off_Z, levels=3 )
    plt.clabel(off_cs, inline=True, fontsize=6)

# display plot
plt.show()
