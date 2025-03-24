
import joblib
import os
import numpy as np
import pandas as pd
# import scikitplot as skplt
import pickle
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier


from sklearn import tree
from sklearn import metrics
from sklearn.metrics import f1_score, cohen_kappa_score, confusion_matrix, accuracy_score, classification_report, multilabel_confusion_matrix


#import matplotlib.pyplot as plt
#import seaborn as sns

curdir = os.getcwd()
RNDSEED = np.random.seed(0)
# !! Double-check path
# C:\Users\iLab\GIT_REPOS\SAFE\S1_TestBed_Demo\S1_TestBed_Demo\code\RandomForestPredictionMQTT
# C:\Users\iLab\GIT_REPOS\SAFE\S1_TestBed_Demo\S1_TestBed_Demo\code\RandomForestModel
# C:\Users\iLab\GIT_REPOS\SAFE\S1_TestBed_Demo\S1_TestBed_Demo\data
# C:\Users\iLab\GIT_REPOS\SAFE\S1_TestBed_Demo\S1_TestBed_Demo\data\ALL_S1_DATA_INT.csv
data_path = r'../../data/ALL_S1_DATA_INT.csv'
data_path = r"../../data/merged_sensor_data_2025_b.csv"
data_path = r"C:\Users\iLab\GIT_REPOS\SAFE\S1_TestBed_Demo\S1_TestBed_Demo\data\CombinedFaults_02222025.csv"

print(f"Curdir: {curdir}")
print(f"Checking at: {data_path}")
df = pd.read_csv(data_path, low_memory=False)

print(df.columns)
# Dropping the timestamp column
df = df[df.columns.drop(list(df.filter(regex = 'timestamp')))]
df = df[df.columns.drop(list(df.filter(regex = 'Unnamed: 0')))]
try:
    df.drop(labels=["Epoch_Seconds"], axis=1, inplace=True)
except Exception as ex:
    print(ex)
# Dropping NaN
df = df.dropna(how = 'any')
print(f"columns: ", df.columns)
# Done to correct python creating an object type by accident since int was never declared when value was swapped
print(df[['status']].describe())
# Setting independent and dependent variables
y = df['status']
x = df.drop('status',axis = 1)

# Train test split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = RNDSEED)
print(x_test)
print(x_train)
print(y_test)
print(y_train)
le = LabelEncoder()
y_train = le.fit_transform(y_train)
y_test = le.fit_transform(y_test)
## Classification
def rf_classification ():
#     rf = RandomForestClassifier(n_estimators = 150, max_depth=50, random_state = RNDSEED)

    rf = RandomForestClassifier(
          min_samples_leaf = 25,
          n_estimators = 150,
          bootstrap = True,
          oob_score = True,
          n_jobs = -1,
          max_features = 12,
          # removed 'auto'
          random_state = RNDSEED
    )
    print("Checking for NaN values in y_train:", pd.Series(y_train).isna().sum())
    print(y_train.dtype)  # Should be int or at least convertible to int
    print(set(y_train))   # Check unique values

    rf.fit(x_train, y_train)

    y_pred = rf.predict(x_test) ## using the untinted dataset!

    return rf, y_pred

def calc_metrics(y_pred, y_true):
    print ('precision_recall_fscore_support \n', metrics.precision_recall_fscore_support(y_pred = y_pred, y_true = y_true, average='micro'))
    print ('confusion_matrix \n', metrics.confusion_matrix(y_pred = y_pred, y_true = y_true))
    print ('metrics.recall_score =>', metrics.recall_score(y_pred = y_pred, y_true = y_true, average = 'micro'))
    print ('cohen_kappa_score => ',  cohen_kappa_score(y_pred,y_true))
    print ('metrics.classification_report \n', metrics.classification_report(y_pred = y_pred, y_true = y_true))
    print ('metrics.matthews_corrcoef =>', metrics.matthews_corrcoef(y_pred = y_pred, y_true = y_true))

rf, y_pred = rf_classification()

calc_metrics(y_pred, y_test)

# save the model
# !! Change to local path
model_path = r"C:\Users\iLab\GIT_REPOS\SAFE\S1_TestBed_Demo\S1_TestBed_Demo\code\RandomForestModel\rf_model\rf02242025_joblib.pk"
# C:\Users\iLab\GIT_REPOS\SAFE\S1_TestBed_Demo\S1_TestBed_Demo\code\RandomForestModel\rf_model
print(f"\n\n\nSaving to: {model_path}")
joblib.dump(rf, model_path)
print(f"\n\n\nLoading from: {model_path}")
loaded_model = joblib.load(model_path)
print('Results after loading the model:')
result = loaded_model.score(x_test, y_test)
print(result)

new_y_pred = loaded_model.predict(x_test)
new_metrics = calc_metrics(new_y_pred, y_test)




