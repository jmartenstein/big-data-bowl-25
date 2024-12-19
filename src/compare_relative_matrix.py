import analyze_play as ap
import pandas as pd
import numpy as np
import sys

def get_player_list_by_team_and_frame(df, team):

    team_rows = df[ df[ "club" ] == team ]
    return team_rows[ "nflId" ].unique()

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

    df_t, df_d = ap.load_tracking_from_game_and_play(game_id, play_id)

    try:
        frame_id = int(sys.argv[3])
    except:
        frame_id = ap.get_frame_id_for_event(df_t, "ball_snap")

    df_f = df_t[ df_t[ "frameId" ] == frame_id ]

    offense_team = df_d[ "possessionTeam" ].values[0]
    defense_team = df_d[ "defensiveTeam" ].values[0]

    off_p_ids = get_player_list_by_team_and_frame(df_f, offense_team)
    offense_rows = df_f[ df_f[ "club" ] == offense_team ]

    def_p_ids = get_player_list_by_team_and_frame(df_f, defense_team)
    defense_rows = df_f[ df_f[ "club" ] == defense_team ]

    compare_field = "y"
    matrix = {}

    # build matrix of values for field
    for i, def_row in defense_rows.iterrows():

        def_field = def_row[ compare_field ]
        field_row = []

        for i, off_row in offense_rows.iterrows():

            off_field = off_row[ compare_field ]
            diff_field = round(abs(def_field - off_field), 2)

            field_row.append(diff_field)

        player_id = def_row[ "nflId" ]
        matrix[ player_id ] = field_row

    df = pd.DataFrame(matrix)
    df.columns = def_p_ids
    df.index = off_p_ids

    df_drop = df.copy()

    min_idxs = []

    # find minimum field values for each row and column
    for i in range(len(df)):

        min_col_idx = df_drop.min().idxmin()
        min_row_idx = df_drop.idxmin()[min_col_idx]

        min_idxs.append([min_row_idx, min_col_idx])

        df_drop.drop( columns = min_col_idx, inplace=True )
        df_drop.drop( index = min_row_idx, inplace=True )


    df_unsorted = df.copy()
    df_sorted_rows = pd.DataFrame([])
    df_sorted = pd.DataFrame([])

    # sort columns
    for i in range(len(df)):

        col_idx = float(min_idxs[i][1])
        df_sorted_rows[col_idx] = df_unsorted[col_idx]
        df_sorted[col_idx] = np.nan

    # sort rows
    for i in range(len(df)):

        row_idx = min_idxs[i][0]
        sorted_row = pd.Series(name=row_idx,
                               data=df_sorted_rows.loc[row_idx].values,
                               index=df_sorted_rows.columns.values)
        df_sorted = pd.concat([df_sorted, sorted_row.to_frame().T])

    print( df_sorted )
