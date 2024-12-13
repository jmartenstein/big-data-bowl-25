import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import numpy as np
import sys
from sklearn.datasets import make_blobs
from sklearn.mixture import GaussianMixture

## FUNCTIONS

def get_unique_labels(df, playername):
    player_frame = df[df["displayName"].isin([playername])]
    unique_clusters = player_frame["labels"].unique()
    unique_clusters.sort()
    return unique_clusters

def get_players_in_cluster(df, idx):
    indexed_players = df[
        (df["labels"] == idx)
    ]
    return indexed_players["displayName"].unique()

def analyze_clusters_in_space(df, players, start_frame, end_frame):

    space_df = df[
        (df["displayName"].isin(players)) & \
        (df["frameId"].isin(range(start_frame,end_frame)))
    ]

    total_points = (end_frame - start_frame) * len(players)
    print(f"Analyzing players {players} across frame range: {start_frame} - {end_frame} ({total_points} total)")
    bins = np.bincount(space_df['labels'])
    count_bool_mask = (bins > 0)
    print(f"{sum(count_bool_mask)} total clusters found in space")
    #print(percentage_array)

    cluster_pct_threshhold = 50

    super_cluster_list = []
    super_cluster_count = 0

    for i in range(len(bins)):
        if bins[i] > 0:
            cluster_df = df[df["labels"] == i]
            percentage = round((bins[i] / len(cluster_df) * 100),2)
            #print(f"Cluster {i} has {bins[i]} of {len(cluster_df)} points in cluster ({percentage}%)")
            if percentage > cluster_pct_threshhold:
                super_cluster_list.append(i)
                super_cluster_count += bins[i]
    #print()

    print(f"{len(super_cluster_list)} clusters found above {cluster_pct_threshhold} threshhold")
    super_cluster_pct = round((super_cluster_count / len(space_df)) * 100)
    print(f"Total of {super_cluster_count} points out of {len(space_df)} ({super_cluster_pct}%)")
    print(f"Clusters: {super_cluster_list}")

    print()

    # Validation 1a: what players are ALSO in the max_idx cluster (besides THill and JJones)?
    idx_max = np.argmax(bins)
    players = get_players_in_cluster(player_pos_df, idx_max)
    #print(f"Players in cluster {idx_max}: {players}")
    #print(f"Largest cluster {idx_max} has {bins[idx_max]} points in the space")
    #print()


### GLOBALS

game_id = 2022091106
play_id = 442
frame_id = 120

# frame 72 - 2 groups
# frame 120 - 3 groups
# frame 155 - 5 or 6 groups?

tracking_file = "data/kaggle/tracking_week_1.csv"
df_tracking = pd.read_csv(tracking_file)

df_focused = df_tracking[
    (df_tracking["playId"] == play_id) & \
    (df_tracking["gameId"] == game_id)
]

# Note: Correlate playerId's for gaussian mixture?

### SET UP DATAFRAMES

df_focused = df_focused[df_focused["club"] != "football"]
df_pos = df_focused[["frameId", "nflId", "displayName", "x", "y"]]
df_motion = df_focused[["frameId", "y", "s","o"]]

#df_motion_only, y_true = make_blobs(n_samples=400, centers=4, cluster_std=0.60, random_state=0)
#X = X[:, ::-1] # flip axes for better plotting

#print(df_motion.shape)
#print(df_motion.sort_values("o"))
#sys.exit(0)

gmm = GaussianMixture(n_components=150,verbose=2).fit(df_motion)
all_labels = gmm.predict(df_motion)
print(all_labels.shape)
print()

player_pos_df = df_pos.copy()
player_pos_df["labels"] = all_labels

# validation 1: what percentage of cells with both THill and JJones are one
# single cluster?
print("### Validation 1 ###")

analyze_clusters_in_space(player_pos_df, ["Tyreek Hill", "Jonathan Jones"], 94, 154)
analyze_clusters_in_space(player_pos_df, ["Tyreek Hill", "Jalen Mills", "Jonathan Jones", "Jaylen Waddle"], 137, 153)

#sys.exit(0)

# validation 2: what clusters include the following players
# Tyreek Hill, Jaylen Waddle, Jonathan Jones, Jalen Mills
print("### Validation 2 ###")
player_names = ["Tyreek Hill", "Jalen Mills", "Jonathan Jones", "Jaylen Waddle"]
print(f"Looking for cluster with players: {player_names}")
intersection_set = []
for p in player_names:
    cluster_list = get_unique_labels(player_pos_df, p)
    if len(intersection_set) == 0:
        intersection_set = cluster_list
    else:
        intersection_set = np.intersect1d(intersection_set, cluster_list)
    #print(f"{p}\t{cluster_list}")

print(f"Intersections with all players: {intersection_set}")
for i in intersection_set:

    players = get_players_in_cluster(player_pos_df, i)
    label_cluster_contents = player_pos_df[player_pos_df["labels"] == i]
    sorted_by_frames = label_cluster_contents.sort_values(by=['frameId'])
    print(f"Cluster {i}: {players}; Size: {sorted_by_frames.shape}")

    #print(sorted_by_frames)
    #print(f"Size: {sorted_by_frames.shape}")


