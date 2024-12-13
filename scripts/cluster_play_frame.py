import pandas as pd
import plotly.figure_factory as ff
from scipy.cluster.hierarchy import dendrogram, linkage

game_id = 2022091106
play_id = 442
frame_id = 120

tracking_file = "data/kaggle/tracking_week_1.csv"

df_tracking = pd.read_csv(tracking_file)

df_focused = df_tracking[
    (df_tracking["playId"] == play_id) & \
    (df_tracking["gameId"] == game_id) & \
    (df_tracking["frameId"] ==frame_id)
]

df_motion_only = df_focused[["x","y","s","a","o","dir"]]
df_motion_only.index = list(df_focused["displayName"])
df_motion_only = df_motion_only.drop(index=["football"])

print(df_motion_only.shape)
#print()
#
#l = linkage(df_motion_only,"ward")

#print(l)
#print(len(l))

#fig = ff.create_dendrogram(df_motion_only,orientation="left",labels=list(df_motion_only.index))
#fig.update_layout(title=f"{game_id},{play_id},{frame_id}")
#fig.show()


