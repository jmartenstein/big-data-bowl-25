import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import numpy as np
import sys
from sklearn.datasets import make_blobs
from sklearn.mixture import GaussianMixture

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
    (df_tracking["gameId"] == game_id) & \
    (df_tracking["frameId"] ==frame_id)
]

df_focused.index = list(df_focused["displayName"])
df_focused = df_focused.drop(index=["football"])


df_pos = df_focused[["x","y"]]
df_motion = df_focused[["s","o"]]
#df_motion_only = df_focused[["x","y","dir"]]

#df_motion_only, y_true = make_blobs(n_samples=400, centers=4, cluster_std=0.60, random_state=0)
#X = X[:, ::-1] # flip axes for better plotting

print(df_motion.sort_values("o"))
#sys.exit(0)

gmm = GaussianMixture(n_components=3,verbose=2).fit(df_motion)
labels = gmm.predict(df_motion)

#probs = gmm.predict_proba(df_motion_only)
#size = 50 * probs.max(1) ** 2
#print(labels)

plt.scatter(df_pos["x"], df_pos["y"], c=labels, cmap='Greys')
plt.show()
