# src/prepare_data.py

# Code to convert / transform raw kaggle data to format
# for machine learning algorithms

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import analyze_play as ap

# get array of games in week 1
df_gs = pd.read_csv("data/kaggle/games.csv")
df_gs_w1 = df_gs[ df_gs["week"] == 1 ]
list_gs_w1 = df_gs_w1[ "gameId" ].unique()

# load player play data for week1
df_ps = pd.read_csv("data/kaggle/plays.csv")
df_total_ps_w1 = df_ps[ ( df_ps["gameId"].isin(list_gs_w1) ) ].copy()

# print total number of play
num_plays = len(df_total_ps_w1)

# remove plays with penalties
df_valid_ps_w1 = df_total_ps_w1[ df_total_ps_w1[ "penaltyYards" ].isnull() ].copy()
penalties_count = num_plays - len(df_valid_ps_w1)
print(f"Total of {num_plays} plays found; removing {penalties_count} "
      f"plays with penalty yardage")
#print(df_nonpenalties_w1.shape)
print()

threshold = 5
df_run_plays = df_valid_ps_w1[ ( df_valid_ps_w1[ "passLength" ].isnull() ) & \
                               ( df_valid_ps_w1[ "yardsGained" ] > threshold ) ].copy()
df_first_down_conversions = df_valid_ps_w1[
    df_valid_ps_w1[ "yardsGained" ] > df_valid_ps_w1[ "yardsToGo" ]
]
#print(f"  Found {len(df_first_down_conversions)} plays with first down conversions")

df_offense_success = df_first_down_conversions.combine_first(df_run_plays)


print(f"Found {len(df_offense_success)} successful offensive plays, combination of:")
print(f"  {len(df_run_plays)} run plays over {threshold} yards gained")
print(f"  {len(df_first_down_conversions)} first down conversions")

# remove duplicates and re-index
df_offense_success = df_offense_success.drop_duplicates()
df_offense_success.reset_index(drop = True)

print(f"After re-indexing, confirmed {len(df_offense_success)} plays")
print()

# defensive success plays: loss of yardage, incomplete passes and turnovers
df_yards_lost = df_valid_ps_w1[ df_valid_ps_w1[ "yardsGained" ] < 0 ]
df_incomplete_passes = df_valid_ps_w1[ df_valid_ps_w1[ "passResult" ] == "I" ]

# get interceptions and sacks
df_interceptions = df_valid_ps_w1[ df_valid_ps_w1[ "passResult" ] == "IN" ]
df_sacks = df_valid_ps_w1[ df_valid_ps_w1[ "passResult" ] == "S" ]

# combine sacks with lost yardage (probably the same?)
df_sacks_and_yards_lost = df_yards_lost.combine_first(df_sacks)
df_defense_success = pd.concat([df_sacks_and_yards_lost, df_interceptions,
                               df_incomplete_passes])

print(f"Found {len(df_defense_success)} successful defensive plays, combination of:")
print(f"  {len(df_incomplete_passes)} incomplete passes")
print(f"  {len(df_yards_lost)} plays with lost yardage")
print(f"  {len(df_sacks)} sacks")
print(f"  {len(df_interceptions)} interceptions")

# remove duplicates and re-index
df_defense_success = df_defense_success.drop_duplicates()
df_defense_success.reset_index(drop = True)

print(f"After re-indexing, confirmed {len(df_defense_success)} plays")
print()

# get unsuccessful plays by combining defense and offense, and finding plays
# not in both sets (left join?)
df_combined_success = pd.concat([ df_offense_success, df_defense_success ])

df_non_ = df_valid_ps_w1.merge(df_combined_success.drop_duplicates(),
                               on=['gameId','playId'],
                               how='left', indicator=True)
df_nonsuccess = df_non_[ df_non_ [ "_merge" ] == "left_only" ]

print(f"Found {len(df_nonsuccess)} unsuccessful plays")
