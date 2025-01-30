
import joblib
import numpy as np
import pandas as pd
# import scikitplot as skplt
import pickle
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor


from sklearn import tree
from sklearn import metrics
from sklearn.metrics import f1_score, cohen_kappa_score, confusion_matrix, accuracy_score, classification_report, multilabel_confusion_matrix

from everywhereml.sklearn.ensemble import RandomForestClassifier
from everywhereml.code_generators.GeneratesCode import GeneratesCode as ml
from everywhereml.code_generators.jinja.Jinja import Jinja
from everywhereml.code_generators.prettifiers.basic_python_prettifier import basic_python_prettify

#import matplotlib.pyplot as plt
#import seaborn as sns

RNDSEED = np.random.seed(0)
# !! Double-check path
df = pd.read_csv('RandomForest/data/ALL_S1_DATA_INT.csv')

print(df.columns)
# Dropping the timestamp column
df = df[df.columns.drop(list(df.filter(regex = 'timestamp')))]
df = df[df.columns.drop(list(df.filter(regex = 'Unnamed: 0')))]
# Dropping NaN
df = df.dropna(how = 'any')
print(df.columns)
# Done to correct python creating an object type by accident since int was never declared when value was swapped

# Setting independent and dependent variables
y = df['status']
x = df.drop('status',axis = 1)

# Train test split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = RNDSEED)

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
joblib.dump(rf, '/Users/jwill521/Desktop/Specific Fault Transitions/RandomForest/model/rf_joblib.z')

loaded_model = joblib.load('/Users/jwill521/Desktop/Specific Fault Transitions/RandomForest/model/rf_joblib.z')
print('Results after loading the model:')
result = loaded_model.score(x_test, y_test)
print(result)

new_y_pred = loaded_model.predict(x_test)
new_metrics = calc_metrics(new_y_pred, y_test)

#print(rf.to_micropython_file('microModel/micro_rf2.mpy'))


