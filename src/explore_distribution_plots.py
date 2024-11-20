import matplotlib.pyplot as plt
import scipy.stats as st
import pandas as pd
import numpy as np

#from sklearn.mixture import GaussianMixture

# set specific frame to analyze
game_id  = 2022091103
play_id  = 1126
frame_id = 100

highlight_player_ids = [46161, 47924]

# load tracking data for the specific frame
df_tr = pd.read_csv("data/kaggle/tracking_week_1.csv")

df_frame = df_tr[ ( df_tr[ "gameId" ] == game_id ) & \
                  ( df_tr[ "playId" ] == play_id ) & \
                  ( df_tr[ "frameId" ] == frame_id )
                ]
#print(df_frame.info)
#print( df_frame[[ "club" ]] )

df_defense_players = df_frame[ df_frame["club"] == "CIN" ]
df_highlight_players = df_frame[ df_frame[ "nflId" ].isin( highlight_player_ids ) ]

# initialize figure and axis
#fig, ax = plt.subplots()


# plot speed arrows

# plot gaussian influence distributions
df_defense_pos = df_defense_players[[ "x", "y" ]]
#dist_defense_pos = GaussianMixture(n_components=1,verbose=2).fit(df_defense_pos)
#print(dist_defense_pos)

mean = np.mean(df_defense_pos, axis=0)
cov = np.cov(df_defense_pos, rowvar=False)

print(f"mean: {mean}")
print(f"cov: {cov}")

list_x = df_defense_pos["x"].values
list_y = df_defense_pos["y"].values

padding = 10
range_x = np.linspace(list_x.min() - padding, list_x.max() + padding)
range_y = np.linspace(list_y.min() - padding, list_y.max() + padding)

X, Y = np.meshgrid(range_x, range_y)
pos = np.dstack((X, Y))
#pos = np.stack((X.ravel(), Y.ravel()), axis=1)

rv = st.multivariate_normal(mean, cov)
Z = rv.pdf(pos)
#Z_unshaped = dist_defense_pos.predict_proba(pos)

#X, Y = np.mgrid[list_x.min():list_x.max(), list_y.min():list_y.max()]
#stack = np.dstack((X, Y))
#print(stack.shape)
#print(X.shape)
#print(Y.shape)
#print(df_defense_pos)

#Z = Z_unshaped.reshape(50, 50)
#print(Z.shape)

#Z_x = Z[:,0]
#Z_x = Z_x.reshape(50, 50)
#Z_y = Z[:,1]
#Z_y = Z_y.reshape(50, 50)


#print(Z_x.shape)
#print(Z_y.shape)

# plot players
plt.xlim((list_x.min() - padding, list_x.max() + padding))
#plt.ylim((list_y.min() - padding, list_y.max() + padding))
plt.ylim(0,54)
plt.title(f"Defensive Players for Frame {frame_id}")

plt.scatter( list_x, list_y )
cs = plt.contour( X, Y, Z, levels=3 )

plt.clabel(cs, inline=True, fontsize=8)

#print(X[5, 5], Y[5,5], Z[5,5])

# display plot
plt.show()

