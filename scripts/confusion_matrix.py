import pandas as pd
import sklearn.metrics as ms

# load test data
df_test = pd.read_csv('data/pass_test_set.csv')

# load result data
df_result = pd.read_csv('data/pass_result_set.csv')

compare_column = 'isPasser'

test_col   = df_test[[ compare_column ]]
result_col = df_result[[ compare_column ]]

acc = ms.accuracy_score(test_col, result_col).round(4)
pre = ms.precision_score(test_col, result_col).round(4)
rec = ms.recall_score(test_col, result_col).round(4)
f1 =  ms.f1_score(test_col, result_col).round(4)

tn, fp, fn, tp = ms.confusion_matrix(test_col, result_col).ravel()

print(f"column: {compare_column}")
print(f"accuracy: {acc}, precision: {pre}, recall: {rec}, f1: {f1}")
print(f"tn: {tn}, fp: {fp}, fn: {fn}, tp: {tp}")
