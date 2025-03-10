# src/prepare_data.py

# Code to convert / transform raw kaggle data to format
# for machine learning algorithms

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import analyze_play as ap

# load player play data for week1
df_ps = pd.read_csv("data/processed/plays_presnap_summary.csv")

# print total number of play
num_plays = len(df_ps)

# remove plays with penalties
df_valid_ps_w1 = df_ps[ df_ps[ "penaltyYards" ].isnull() ].copy()
penalties_count = num_plays - len(df_valid_ps_w1)
print(f"Total of {num_plays} plays found; removing {penalties_count} "
      f"plays with penalty yardage")
print()

threshold = 5
df_run_plays = df_valid_ps_w1[ ( df_valid_ps_w1[ "passLength" ].isnull() ) & \
                               ( df_valid_ps_w1[ "yardsGained" ] > threshold ) ].copy()
df_first_down_conversions = df_valid_ps_w1[
    df_valid_ps_w1[ "yardsGained" ] > df_valid_ps_w1[ "yardsToGo" ]
]

df_offense_success = df_first_down_conversions.combine_first(df_run_plays)


print(f"Found {len(df_offense_success)} successful offensive plays, combination of:")
print(f"  {len(df_run_plays)} run plays over {threshold} yards gained")
print(f"  {len(df_first_down_conversions)} first down conversions")

df_offense_success['offenseTarget'] = 1
df_offense_success['defenseTarget'] = 0
df_offense_success['targetDiff'] = 1

# remove duplicates and re-index
df_offense_success = df_offense_success.drop_duplicates()
df_offense_success.reset_index(drop = True)

print(f"After re-indexing, confirmed {len(df_offense_success)} plays")
print(f"  Offense success shape: {df_offense_success.shape}")
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

df_defense_success['offenseTarget'] = 0
df_defense_success['defenseTarget'] = 1
df_defense_success['targetDiff'] = -1

print(f"Found {len(df_defense_success)} successful defensive plays, combination of:")
print(f"  {len(df_incomplete_passes)} incomplete passes")
print(f"  {len(df_yards_lost)} plays with lost yardage")
print(f"  {len(df_sacks)} sacks")
print(f"  {len(df_interceptions)} interceptions")

# remove duplicates and re-index
df_defense_success = df_defense_success.drop_duplicates()
df_defense_success.reset_index(drop = True)

print(f"After re-indexing, confirmed {len(df_defense_success)} plays")
print(f"  Defense success shape: {df_defense_success.shape}")
print()


# get unsuccessful plays by combining defense and offense, and finding plays
# not in both sets (left join?)
df_combined_success = pd.concat([ df_offense_success, df_defense_success ])

df_non_ = df_valid_ps_w1.merge(df_combined_success.drop_duplicates(),
                               on=['gameId','playId'],
                               how='left', indicator=True)
df_nonsuccess = df_non_[ df_non_ [ "_merge" ] == "left_only" ].copy()

df_nonsuccess['maxOffenseSpeed'] = df_nonsuccess['maxOffenseSpeed_x']
df_nonsuccess['maxDefenseSpeed'] = df_nonsuccess['maxDefenseSpeed_x']
df_nonsuccess['offenseDistanceTraveled'] = df_nonsuccess['offenseDistanceTraveled_x']
df_nonsuccess['defenseDistanceTraveled'] = df_nonsuccess['defenseDistanceTraveled_x']
df_nonsuccess['elapsedTime'] = df_nonsuccess['elapsedTime_x']

df_nonsuccess['offenseTarget'] = 0
df_nonsuccess['defenseTarget'] = 0
df_nonsuccess['targetDiff' ] = 0

print(f"Found {len(df_nonsuccess)} unsuccessful plays")
print(f"  Non success shape: {df_nonsuccess.shape}")
print()

df_concat = pd.concat([df_offense_success, df_defense_success, df_nonsuccess])

feature_columns = [ 'gameId',
                    'playId',
                    'maxOffenseSpeed',
                    'maxDefenseSpeed',
                    'offenseDistanceTraveled',
                    'defenseDistanceTraveled',
                    'elapsedTime',
                    'offenseTarget',
                    'defenseTarget',
                    'targetDiff'
                  ]
df_targets_week1 = df_concat[ feature_columns ]

print(f"Writing data with shape {df_targets_week1.shape} to csv file")

df_targets_week1.to_csv('data/processed/plays_and_targets.csv', index=False)
