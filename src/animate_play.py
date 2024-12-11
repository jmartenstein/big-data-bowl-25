"""
A script that animates tracking data, given gameId and playId.
Players can be identified by mousing over the individuals dots.
The play description is also displayed at the bottom of the plot,
together with play information at the top of the plot.

Original Source: https://github.com/mpchang/uncovering-missed-tackle-opportunities/blob/main/code/plotting/animate_play.py

Original Source: https://www.kaggle.com/code/huntingdata11/animated-and-interactive-nfl-plays-in-plotly/notebook
"""

import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np

import sys

pio.renderers.default = (
    "browser"  # modify this to plot on something else besides browser
)

data_dir = "./data/kaggle"

# Modify the variables below to plot your desired play
tracking_prefix = data_dir + "/tracking_week_"
plays_file = data_dir + "/plays.csv"
games_file = data_dir + "/games.csv"
players_file = data_dir + "/players.csv"

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

# Test cases:

# 2022092503,2132
# 2022091113,1363; TB at DAL; interception
# 2022091113,3853; TB at DAL
# 2022091106,442;  MIA at NE
# 2022091200,109;  DEN at SEA
# 2022103003,612;  MIA at DET

# team colors to distinguish between players on plots
colors = {
    "ARI": "#97233F",
    "ATL": "#A71930",
    "BAL": "#241773",
    "BUF": "#00338D",
    "CAR": "#0085CA",
    "CHI": "#C83803",
    "CIN": "#FB4F14",
    "CLE": "#311D00",
    "DAL": "#003594",
    "DEN": "#FB4F14",
    "DET": "#0076B6",
    "GB": "#203731",
    "HOU": "#03202F",
    "IND": "#002C5F",
    "JAX": "#9F792C",
    "KC": "#E31837",
    "LA": "#FFA300",
    "LAC": "#0080C6",
    "LV": "#000000",
    "MIA": "#008E97",
    "MIN": "#4F2683",
    "NE": "#002244",
    "NO": "#D3BC8D",
    "NYG": "#0B2265",
    "NYJ": "#125740",
    "PHI": "#004C54",
    "PIT": "#FFB612",
    "SEA": "#69BE28",
    "SF": "#AA0000",
    "TB": "#D50A0A",
    "TEN": "#4B92DB",
    "WAS": "#5A1414",
    "football": "#CBB67C",
    "tackle": "#FFC0CB",
}

position_groups = {
    "Backs & Receivers": ["QB", "WR", "RB", "FB", "TE"],
    "Offensive Line":    ["C", "G", "T"],
    "Defense":           ["NT", "CB", "DT", "DE", "DB", "LB", "MLB", "ILB", "OLB", "SS", "FS"],
    "Football":          ["football"]
}

# Handle Data I/O
df_game = pd.read_csv(games_file)
df_plays = pd.read_csv(plays_file)
df_players = pd.read_csv(players_file)

try:
    week_number = df_game[(df_game["gameId"] == game_id)]["week"].values[0]
except:
    print("Could not find week for game")
    sys.exit(1)

tracking_file = tracking_prefix + str(week_number) + ".csv"
df_tracking_unmerged = pd.read_csv(tracking_file)

# add footbal to players dataset
df_tracking_unmerged[[ "nflId" ]] = df_tracking_unmerged[[ "nflId" ]].fillna(-1)
df_players.loc[-1] = { 'nflId': -1, 'position': 'football' }
df_players.index = df_players.index + 1
df_players = df_players.sort_index()

# merge player positions into tracking data
df_player_positions = df_players[[ "nflId", "position" ]]
df_tr = df_tracking_unmerged.merge(df_player_positions, on=['nflId'])
df_full_tracking = df_tr.merge(df_plays, on=["gameId", "playId"])

df_focused = df_full_tracking[
    (df_full_tracking["playId"] == play_id) & (df_full_tracking["gameId"] == game_id)
]

# Get General Play Information
absolute_yd_line = df_focused.absoluteYardlineNumber.values[0]
play_going_right = (
    df_focused.playDirection.values[0] == "right"
)  # 0 if left, 1 if right

line_of_scrimmage = absolute_yd_line

# place LOS depending on play direction and absolute_yd_line. 110 because absolute_yd_line includes endzone width

first_down_marker = (
    (line_of_scrimmage + df_focused.yardsToGo.values[0])
    if play_going_right
    else (line_of_scrimmage - df_focused.yardsToGo.values[0])
)  # Calculate 1st down marker

down = df_focused.down.values[0]
quarter = df_focused.quarter.values[0]
gameClock = df_focused.gameClock.values[0]
playDescription = df_focused.playDescription.values[0]
lineset_frame_id = -1

# Handle case where we have a really long Play Description and want to split it into two lines
if len(playDescription.split(" ")) > 15 and len(playDescription) > 115:
    playDescription = (
        " ".join(playDescription.split(" ")[0:16])
        + "<br>"
        + " ".join(playDescription.split(" ")[16:])
    )

print(
    f"Line of Scrimmage: {line_of_scrimmage}, First Down Marker: {first_down_marker}, Down: {down}, Quarter: {quarter}, Game Clock: {gameClock}, Play Description: {playDescription}"
)

# initialize plotly play and pause buttons for animation
updatemenus_dict = [
    {
        "buttons": [
            {
                "args": [
                    None,
                    {
                        "frame": {"duration": 100, "redraw": False},
                        "fromcurrent": True,
                        "transition": {"duration": 0},
                    },
                ],
                "label": "Play",
                "method": "animate",
            },
            {
                "args": [
                    [None],
                    {
                        "frame": {"duration": 0, "redraw": False},
                        "mode": "immediate",
                        "transition": {"duration": 0},
                    },
                ],
                "label": "Pause",
                "method": "animate",
            },
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 87},
        "showactive": False,
        "type": "buttons",
        "x": 0.1,
        "xanchor": "right",
        "y": 0,
        "yanchor": "top",
    }
]

# initialize plotly slider to show frame position in animation
sliders_dict = {
    "active": 0,
    "yanchor": "top",
    "xanchor": "left",
    "currentvalue": {
        "font": {"size": 20},
        "prefix": "Frame:",
        "visible": True,
        "xanchor": "right",
    },
    "transition": {"duration": 300, "easing": "cubic-in-out"},
    "pad": {"b": 10, "t": 50},
    "len": 0.9,
    "x": 0.1,
    "y": 0,
    "steps": [],
}

# Frame Info
sorted_frame_list = df_focused.frameId.unique()
sorted_frame_list.sort()

frames = []
for frameId in sorted_frame_list:
    data = []
    # Add Yardline Numbers to Field
    data.append(
        go.Scatter(
            x=np.arange(20, 110, 10),
            y=[5] * len(np.arange(20, 110, 10)),
            mode="text",
            text=list(
                map(str, list(np.arange(20, 61, 10) - 10) + list(np.arange(40, 9, -10)))
            ),
            textfont_size=30,
            textfont_family="Courier New, monospace",
            textfont_color="#ffffff",
            showlegend=False,
            hoverinfo="none",
        )
    )
    data.append(
        go.Scatter(
            x=np.arange(20, 110, 10),
            y=[53.5 - 5] * len(np.arange(20, 110, 10)),
            mode="text",
            text=list(
                map(str, list(np.arange(20, 61, 10) - 10) + list(np.arange(40, 9, -10)))
            ),
            textfont_size=30,
            textfont_family="Courier New, monospace",
            textfont_color="#ffffff",
            showlegend=False,
            hoverinfo="none",
        )
    )
    # Add line of scrimage
    data.append(
        go.Scatter(
            x=[line_of_scrimmage, line_of_scrimmage],
            y=[0, 53.5],
            line_dash="dash",
            line_color="blue",
            showlegend=False,
            hoverinfo="none",
        )
    )
    # Add First down line
    data.append(
        go.Scatter(
            x=[first_down_marker, first_down_marker],
            y=[0, 53.5],
            line_dash="dash",
            line_color="yellow",
            showlegend=False,
            hoverinfo="none",
        )
    )

    # Plot Players
    plot_df = df_focused[
        (df_focused.frameId == frameId)
    ].copy()

    # get frame for Line Set event
    if plot_df.event.values[0] == 'line_set':
        lineset_frame_id = frameId

    # because football doesn't have an nflId, we're going to insert one
    # we assume each frame only has a single football
    football_idx = plot_df.index[plot_df['club']=='football'].values[0]
    plot_df.at[football_idx, 'nflId'] = 0

    p_dir = 0

    # For the purposes of the plotly scatter, we have positional groups,
    # which allow us to select and deselect different groups on the plot

    for group, positions in position_groups.items():

        pos_group_df = plot_df[ plot_df["position"].isin(positions) ]

        hover_text_array = []
        position_group_array = []
        player_color_array = []

        for nflId in pos_group_df.nflId:

            selected_player_df = pos_group_df[pos_group_df.nflId == nflId]

            p_id = int(selected_player_df['nflId'].values[0])
            p_name = selected_player_df['displayName'].values[0]
            p_speed = selected_player_df['s'].values[0]
            p_pos = selected_player_df['position'].values[0]

            hover_text = f"id: {str(p_id)}, pos: {p_pos}<br>" + \
                         f"name: {p_name}<br>" + \
                         f"spd: {p_speed} yd/sec<br>"
            hover_text_array.append(hover_text)

            color = colors[pos_group_df['club'].values[0]]
            player_color_array.append(color)

        data.append(
            go.Scatter(
                x=pos_group_df["x"],
                y=pos_group_df["y"],
                mode="markers",
                marker_color=player_color_array,
                marker_size=10,
                name=group,
                hovertext=hover_text_array,
                hoverinfo="text",
            )
        )

    # add frame to slider
    slider_step = {
        "args": [
            [frameId],
            {
                "frame": {"duration": 100, "redraw": False},
                "mode": "immediate",
                "transition": {"duration": 0},
            },
        ],
        "label": str(frameId),
        "method": "animate",
    }
    sliders_dict["steps"].append(slider_step)
    frames.append(go.Frame(data=data, name=str(frameId)))

scale = 10
layout = go.Layout(
    autosize=False,
    width=120 * scale,
    height=60 * scale,
    xaxis=dict(
        range=[0, 120],
        autorange=False,
        tickmode="array",
        tickvals=np.arange(10, 111, 5).tolist(),
        showticklabels=False,
    ),
    yaxis=dict(range=[0, 53.3], autorange=False, showgrid=False, showticklabels=False),
    plot_bgcolor="#00B140",
    # Create title and add play description at the bottom of the chart for better visual appeal
    title=f"GameId: {game_id}, PlayId: {play_id}<br>{gameClock} {quarter}Q, Line Set at Frame {lineset_frame_id}"
    + "<br>" * 19
    + f"{playDescription}",
    updatemenus=updatemenus_dict,
    sliders=[sliders_dict],
)

fig = go.Figure(data=frames[0]["data"], layout=layout, frames=frames[1:])

# Create First Down Markers
for y_val in [0, 53]:
    fig.add_annotation(
        x=first_down_marker,
        y=y_val,
        text=str(down),
        showarrow=False,
        font=dict(family="Courier New, monospace", size=16, color="black"),
        align="center",
        bordercolor="black",
        borderwidth=2,
        borderpad=4,
        bgcolor="#ff7f0e",
        opacity=1,
    )

fig.show()
