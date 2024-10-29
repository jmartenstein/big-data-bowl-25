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

### SET UP DATAFRAMES

df_focused = df_focused[df_focused["club"] != "football"]
df_pos = df_focused[["frameId", "nflId", "displayName", "x", "y"]]
df_motion = df_focused[["frameId", "y", "s","o"]]
#df_motion_only = df_focused[["x","y","dir"]]

#df_motion_only, y_true = make_blobs(n_samples=400, centers=4, cluster_std=0.60, random_state=0)
#X = X[:, ::-1] # flip axes for better plotting

print(df_motion.shape)
#print(df_motion.sort_values("o"))
#sys.exit(0)

gmm = GaussianMixture(n_components=48,verbose=2).fit(df_motion)
all_labels = gmm.predict(df_motion)
print(all_labels.shape)
print()

player_pos_df = df_pos.copy()
player_pos_df["labels"] = all_labels

# validation 1: what percentage of cells with both THill and JJones are one
# single cluster?
print("### Validation 1 ###")
man_coverage_frames = player_pos_df[
    (player_pos_df["displayName"].isin(["Tyreek Hill", "Jonathan Jones"])) & \
    (player_pos_df["frameId"].isin(range(94,154)))
]

bins = np.bincount(man_coverage_frames['labels'])
idx_max = np.argmax(bins)
print(f"Cluster {idx_max} has {bins[idx_max]} player/frame matches out of {len(man_coverage_frames['labels'])} total")
median_bool_mask = (man_coverage_frames['labels'] == idx_max)
probability = median_bool_mask.sum() / len(median_bool_mask)
print(f"prob:    {probability}")

# Validation 1a: what players are ALSO in the max_idx cluster (besides THill and JJones)?
players = get_players_in_cluster(player_pos_df, idx_max)
print(f"Cluster {idx_max}: {players}")
print()

# validation 2: what clusters have ONLY the following players
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
    print(f"Cluster {i}: {players}")

    label_cluster_contents = player_pos_df[player_pos_df["labels"] == i]
    sorted_by_frames = label_cluster_contents.sort_values(by=['frameId'])
    print(sorted_by_frames)
    print(sorted_by_frames.shape)


