import matplotlib.pyplot as plt
import scipy.stats as st
import pandas as pd
import numpy as np

def calc_team_dist(df_players):

    df_players_pos = df_players[[ "x", "y" ]]
    mean = np.mean(df_players_pos, axis=0)
    cov = np.cov(df_players_pos, rowvar=False)

    return mean, cov

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

def generate_mesh_grid(max_x, min_x, max_y, min_y):

    range_x = np.linspace(min_x, max_x)
    range_y = np.linspace(min_y, max_y)

    X, Y = np.meshgrid(range_x, range_y)

    return X, Y

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

def score_z_values(X, Y, mean, cov, weight=1):

    pos = np.dstack((X, Y))
    rv = st.multivariate_normal(mean, cov)

    Z_pre = rv.pdf(pos)
    Z = [ (weight * x) for x in Z_pre ]

    Z_mean = rv.pdf(mean) * weight
    print_point_and_value(mean["x"], mean["y"], Z_mean)

    #print(Z[mean[0], mean[1]])

    return Z

# set specific frame to analyze
game_id  = 2022091103
play_id  = 1126
frame_id = 85

#highlight_player_ids = [46161, 47924]

# load tracking data for the specific frame
df_tr = pd.read_csv("data/kaggle/tracking_week_1.csv")

df_frame = df_tr[ ( df_tr[ "gameId" ] == game_id ) & \
                  ( df_tr[ "playId" ] == play_id ) & \
                  ( df_tr[ "frameId" ] == frame_id )
                ]

df_defense_players = df_frame[ df_frame["club"] == "CIN" ]
df_offense_players = df_frame[ df_frame["club"] == "PIT" ]
df_highlight_players = df_frame[ df_frame[ "nflId" ].isin( highlight_player_ids ) ]

# plot speed arrows

# plot gaussian influence distributions
def_mean, def_cov = calc_team_dist(df_defense_players)
off_mean, off_cov = calc_team_dist(df_offense_players)

max_x, min_x, max_y, min_y = find_frame_boundaries(df_frame, 5, True)
X, Y = generate_mesh_grid(max_x, min_x, max_y, min_y)

print("Defense")
def_Z = score_z_values(X, Y, def_mean, def_cov, 256.67)
print("Offense")
off_Z = score_z_values(X, Y, off_mean, off_cov, -88.91)

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
