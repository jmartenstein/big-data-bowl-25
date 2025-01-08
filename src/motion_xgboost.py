import pandas as pd
import analyze_play as ap
import seaborn as sns
import matplotlib.pyplot as plt
import sklearn.metrics as ms

import glob

from xgboost import XGBClassifier
from sklearn import model_selection


def motiondir_to_int( df_row ):
    if (df_row[ "motionDirRelativeToScrimmage" ] == "back"):
        return 1
    else:
        return 0

def isdropback_to_int( df_row ):
    if (df_row["isDropback"]):
        return 1
    else:
        return 0

def merge_motion_and_play_dataframes( df_m, df_p ):
    df_merged = df_m.merge( df_p, on=[ 'gameId', 'playId' ] )
    return df_merged

motion_filename = f"{ap.PROCESSED_DATA_DIR}/motion.week4.20250102.22*"
#motion_filename  = f"{ap.PROCESSED_DATA_DIR}/motion.2022091102.2025*"
plays_filename   = f"{ap.RAW_DATA_DIR}/plays.csv"

motion_files_found = glob.glob(motion_filename)
if len(motion_files_found) > 1:
    print(f"ERROR: Motion file {motion_filename} is not specific enough; " \
          f"found {len(motion_files_found)} files")
    sys.exit(1)

df_motion = pd.read_csv(motion_files_found[0])
df_plays  = pd.read_csv(plays_filename)

df_merged = merge_motion_and_play_dataframes(df_motion, df_plays)

df_merged["motionDirToInt"]  =  df_merged.apply(motiondir_to_int, axis = 1)
df_merged["isDropbackToInt"] =  df_merged.apply(isdropback_to_int, axis = 1)

df = df_merged[ df_merged[ "isDefense" ] == True ]

print(f"Shape: {df.shape}")
#print(f"Columns: {df.columns}")

features = [ "nflId", "vectorX", "vectorY", "finalX", "finalY", "dirOffest",
             "motionDirToInt", "totalDistance", "absSpeed" ]
target = "isDropbackToInt"

# split the data into train and test sections
X_train, X_test, y_train, y_test = model_selection.train_test_split(
    df[features], df[target], test_size = .2)

# create the classifier model and then fit the model
boost = XGBClassifier(n_estimators=2, max_depth=2, learning_rate=1, objective='binary:logistic')
boost.fit(X_train, y_train)

# make predictions on the X_test dataset
y_preds = boost.predict(X_test)

feature_importance = boost.get_booster().get_score(importance_type='gain')
print(feature_importance)

# calculate the confusion matrix to understand the model accuracy
cm = ms.confusion_matrix(y_test, y_preds)

# Extract true positives (TP) and false positives (FP) from the confusion matrix
tp = cm[1, 1]
fp = cm[0, 1]

# Calculate precision
precision = tp / (tp + fp)

print(f"Precision: {precision}")

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')

plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix')

plt.show()
