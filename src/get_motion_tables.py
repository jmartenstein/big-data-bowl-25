import pandas as pd
import analyze_play as ap

import glob

def summarize_positions( row ):

    #pos = row["position"]
    summary_hash = {
        'CB':  'Cornerbacks',
        'SS':  'Safeties',
        'FS':  'Safeties',
        'ILB': 'Linebackers',
        'OLB': 'Linebackers',
        'MLB': 'Linebackers',
        'LB':  'Linebackers'
    }
    try:
        pos_summary = summary_hash[ row[ "position" ] ]
    except:
        pos_summary = "Other"

    return pos_summary

motion_filename      = f"{ap.PROCESSED_DATA_DIR}/motion.week4.20250105*"

motion_files_found = glob.glob(motion_filename)
if len(motion_files_found) > 1:
    print(f"ERROR: Motion file {motion_filename} is not specific enough; " \
          f"found {len(motion_files_found)} files")
    sys.exit(1)

df_motion = pd.read_csv(motion_files_found[0])

#print(df_motion.columns.values)
unique_positions = df_motion["position"].unique()
#print(unique_positions)
df_motion['pos_summary'] = df_motion.apply(summarize_positions, axis=1)

df_pos_counts = df_motion[['pos_summary']]
#df_pos_counts = pd.DataFrame(position_counts)
df_pos_counts.columns = ['Positions']

#df_pos_counts.drop(['pos_summary'], inplace=True)
#df_pos_counts.drop(['Other'], inplace=True)

#df_pos_counts.style.background_gradient(cmap='Blues')
print(df_pos_counts.index)
