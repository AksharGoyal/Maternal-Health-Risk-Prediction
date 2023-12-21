from ucimlrepo import fetch_ucirepo 
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score as acc
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder
import numpy as np

def clean_data(df):
    '''
    Cleans the data before used for training our model
    '''
    df_cols = df.columns
    _, column = df.shape
    # remove null values
    keep_cols = []
    for col in df_cols:
        if ((df[col].isna().sum()/column)*100) > 50:
            continue
        keep_cols.append(col)
    
    df_new = df.loc[:, keep_cols]
    
    # impute misisng values
    num_cols = df_new.select_dtypes(include='number').columns
    cat_cols = df_new.select_dtypes(exclude='number').columns
    # print(df_new.columns,'\n')
    df_new = df_new.loc[~(df_new.Management.isna() | df_new.Severity.isna() | df_new.Diagnosis.isna())]
    df_new.dropna(thresh=5, inplace=True)

    for col in num_cols:
        df_new.loc[df_new[col].isna(), col] = df_new[col].mean()
        if col in ['Length_of_Stay', 'Thrombocyte_Count', 'CRP', 'US_Number', 'Age']:
            df_new[col] = df_new[col].astype(int)

    for col in cat_cols:
        df_new[col] = df_new[col].astype('category')
        df_new.loc[df_new[col].isna(), col] = df_new[col].mode()[0]
        
    # Remove outlier values
    df_new = df_new.loc[df_new.Stool != 'constipation, diarrhea', :]
    df_new = df_new.loc[df.Management != 'simultaneous appendectomy', :]
    target = df_new.loc[:, 'Diagnosis']
    df_new = df_new[['Weight', 'Sex', 'Length_of_Stay', 'Appendix_on_US', 'Migratory_Pain', 'Lower_Right_Abd_Pain',
       'Contralateral_Rebound_Tenderness', 'Coughing_Pain', 'Nausea', 'Loss_of_Appetite', 'Body_Temperature',
       'WBC_Count', 'RBC_Count', 'Hemoglobin', 'RDW', 'Thrombocyte_Count', 'CRP', 'Stool', 'Peritonitis', 'US_Number']]
    # df_new = df_new[['Length_of_Stay', 'RBC_Count', 'WBC_Count', 'Weight', 'Thrombocyte_Count', 'Body_Temperature',
    #                  'Appendix_on_US', 'CRP', 'Peritonitis', 'Hemoglobin']]
    return df_new, target

regensburg_pediatric_appendicitis = fetch_ucirepo(id=938)
X = regensburg_pediatric_appendicitis.data.features 
y = regensburg_pediatric_appendicitis.data.targets 
df = pd.concat([X, y], axis=1)

X, target = clean_data(df)

dv = DictVectorizer(sparse=False)
le = LabelEncoder()
y = le.fit_transform(target)

X_train, X_test, y_train, y_test = train_test_split(X, target, train_size=0.6, random_state=42)

X_train_dv = dv.fit_transform(X_train.to_dict(orient='records'))
X_test_dv = dv.transform(X_test.to_dict(orient='records'))

rfc = RandomForestClassifier(max_depth=10, random_state=42, n_estimators=100)

rfc.fit(X_train_dv, y_train)
y_pred = rfc.predict(X_test_dv)
print(f"Accuracy: {acc(y_test, y_pred)}")

with open('rfc.bin', 'wb') as f:
    pickle.dump(rfc, f)
with open('dv.bin', 'wb') as f:
    pickle.dump(dv, f)
with open('le.bin', 'wb') as f:
    pickle.dump(le, f)