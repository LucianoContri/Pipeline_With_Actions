import os
import random
import numpy as np
import random as python_random
import tensorflow
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, InputLayer
from keras.utils import to_categorical


import pandas as pd
import matplotlib.pyplot as plt
import mlflow
import dagshub
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

"""# Definindo funções adicionais"""

def reset_seeds():
   os.environ['PYTHONHASHSEED']=str(42)
   tf.random.set_seed(42)
   np.random.seed(42)
   random.seed(42)

"""# 2 - Fazendo a leitura do dataset e atribuindo às respectivas variáveis"""
def read_data():
    data = pd.read_csv('https://raw.githubusercontent.com/renansantosmendes/lectures-cdas-2023/master/fetal_health_reduced.csv')
    X=data.drop(["fetal_health"], axis=1)
    y=data["fetal_health"]
    return X, y

def process_data(X, y):
    columns_names = list(X.columns)
    scaler = preprocessing.StandardScaler()
    X_df = scaler.fit_transform(X)
    X_df = pd.DataFrame(X_df, columns=columns_names)

    X_train, X_test, y_train, y_test = train_test_split(X_df,
                                                        y,
                                                        test_size=0.3,
                                                        random_state=42)

    y_train = y_train -1
    y_test = y_test - 1

    return X_train, X_test, y_train, y_test

def create_model(X):
    reset_seeds()
    model = Sequential()
    model.add(InputLayer(input_shape=(X.shape[1], )))
    model.add(Dense(10, activation='relu'))
    model.add(Dense(10, activation='relu'))
    model.add(Dense(3, activation='softmax'))
    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    return model


def config_mlflow():

    # Set DagsHub credentials using environment variables from GitHub Actions secrets
    os.environ['MLFLOW_TRACKING_USERNAME'] = os.getenv('DAGSHUB_USERNAME')  # Username from secrets
    os.environ['MLFLOW_TRACKING_PASSWORD'] = os.getenv('DAGSHUB_TOKEN')
    # Set MLflow tracking URI to DagsHub's MLflow instance
    mlflow.set_tracking_uri('https://dagshub.com/LucianoContri/Data-Science-and-Big-data.mlflow')

    # Enable TensorFlow autologging
    mlflow.tensorflow.autolog(log_models=True,
                              log_input_examples=True,
                              log_model_signatures=True)

def train_model(model, X_train, y_train, is_train=True):
    # Start an MLflow run for logging
    with mlflow.start_run(run_name='experiment_mlops_ead') as run:
        model.fit(X_train,
                  y_train,
                  epochs=50,
                  validation_split=0.2,
                  verbose=3)
    if is_train:
        run_uri = f'runs:/{run.info.run_id}'
        mlflow.register_model(run_uri, 'fetal_health')

if __name__ == '__main__':
     # Token from secrets

    # Assuming `read_data`, `process_data`, and `create_model` functions are defined elsewhere in your code
    X, y = read_data()  # Load your data
    X_train, X_test, y_train, y_test = process_data(X, y)  # Process your data
    model = create_model(X_train)  # Create your model

    # Configure MLflow with DagsHub
    config_mlflow()

    # Train the model and log to MLflow/DagsHub
    train_model(model, X_train, y_train)