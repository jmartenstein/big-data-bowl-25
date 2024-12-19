import analyze_play as ap
import pandas as pd
import sys

ap.DATA_DIR = 'data/kaggle'

if __name__  == '__main__':

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

    df_pp_ = pd.read_csv("data/kaggle/player_play.csv")
    df_pp_ = df_pp_[ ( df_pp_[ "playId" ] == play_id ) & \
                    ( df_pp_[ "gameId" ] == game_id )
                  ]
    df_pp = df_pp_[[ "nflId",
                     "pff_primaryDefensiveCoverageMatchupNflId",
                     "pff_secondaryDefensiveCoverageMatchupNflId"
                  ]].copy()

    df_pp.rename( columns = { "pff_primaryDefensiveCoverageMatchupNflId": "primary_id",
                              "pff_secondaryDefensiveCoverageMatchupNflId": "secondary_id"
                            },
                  inplace = True
                )

    df_ps_ = pd.read_csv("data/kaggle/players.csv")
    df_ps = df_ps_[[ "nflId", "displayName" ]]

    df_name_merge = df_pp.merge( df_ps, on=["nflId"] )
    df_primary_merge = df_name_merge.merge( df_ps,
                                            how="left",
                                            left_on=["primary_id"],
                                            right_on=["nflId"])
    df_primary_merge.rename( columns = { 'displayName_x': 'player_name',
                                         'displayName_y': 'primary_name',
                                         'nflId_x': 'player_id'
                                       },
                             inplace = True )
    df_merged = df_primary_merge.merge( df_ps,
                                        how="left",
                                        left_on=["secondary_id"],
                                        right_on=["nflId"] )
    df_merged.rename( columns = { 'displayName': 'secondary_name' },
                      inplace = True )
    df_merged.sort_values( by = ['secondary_id', 'primary_id'], inplace = True )

    df_sort_columns = df_merged[[ "player_name", "player_id", "primary_name", "primary_id",
                                  "secondary_name", "secondary_id" ]]
    df_sort_columns = df_sort_columns[ df_sort_columns[ "primary_id" ].notnull() ]
    print(df_sort_columns.to_string(index=False))


