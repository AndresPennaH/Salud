# -*- coding: utf-8 -*-
"""Copia de Salud.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17Ul0F_HiVs3diRq8xJ5cFCnz951-S4UF
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import spatial 
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from matplotlib.pyplot import figure
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

from google.colab import drive
drive.mount('/content/drive')

aplsalud = pd.read_csv('/content/drive/MyDrive/Analítica 3 para dummies /Trabajo aplicaciones salud/diabetes_data.csv')
aplsalud.tail(10)

print(aplsalud.shape)                    
print(aplsalud.columns)                  
print(aplsalud.dtypes)

# Revision nulos
aplsalud.isnull().sum()

# frecuencia de categoria
print(aplsalud['Stroke'].value_counts())
print(aplsalud['HighBP'].value_counts())
print(aplsalud['Diabetes'].value_counts())

aplsalud.drop('CholCheck', axis=1, inplace=True)

aplsalud2 = aplsalud.copy()

from sklearn.preprocessing import MinMaxScaler
# Crear un objeto MinMaxScaler
scaler = MinMaxScaler()

# Seleccionar las columnas a escalar
columnas_escalar = ['BMI','GenHlth', 'MentHlth', 'PhysHlth']

# Escalar las columnas seleccionadas
aplsalud2[columnas_escalar] = scaler.fit_transform(aplsalud[columnas_escalar])
aplsalud2

#HEAT MAP
figure(figsize= (20,15),dpi=80);
sns.heatmap(aplsalud2.corr(),annot = True);
plt.title("Mapa de calor correlaciones variables", fontsize =20);

"""## **Analisis exploratorio**"""

# Diabetes segun estado de salud 
base1 = aplsalud[aplsalud['Diabetes']==1].groupby(['GenHlth'])[['Diabetes']].count().reset_index()

dic = {1:'Excelente',
       2:'Muy buena',
       3:'Buena',
       4:'Regular',
       5:'Mala'}
base1['GenHlth'] = base1['GenHlth'].replace(dic)

# crear gráfica:
fig = px.pie(base1, values = 'Diabetes', names ='GenHlth',
             title= '<b>Diabetes por estado de salud<b>',
             color_discrete_sequence=px.colors.qualitative.D3)

# agregar detalles a la gráfica:
fig.update_layout(
    template = 'simple_white',
    title_x = 0.5)

fig.show()

# Diabetes segun edad
base2 = aplsalud[aplsalud['Diabetes']==1].groupby(['Age'])[['Diabetes']].count().sort_values('Diabetes', ascending = False).reset_index()

# crear gráfica
fig = px.bar(base2, x = 'Age', y='Diabetes',
             title= '<b>Diabetes segun edad<b>',
             color_discrete_sequence=px.colors.qualitative.G10)

# agregar detalles a la gráfica
fig.update_layout(
    template = 'simple_white',
    title_x = 0.5)

fig.show()

# Diabetes de acuerdo al genero 
base3 = aplsalud[aplsalud['Diabetes']==1].groupby(['Sex'])[['Diabetes']].count().reset_index()

# crear gráfica:
fig = px.pie(base3, values = 'Diabetes', names ='Sex',
             title= '<b>Diabetes por género<b>',
             color_discrete_sequence=px.colors.qualitative.D3)

# agregar detalles a la gráfica:
fig.update_layout(
    template = 'simple_white',
    title_x = 0.5)

fig.show()

# definir gráfica

aplsalud_d = aplsalud[aplsalud['Diabetes']==1]
fig = px.histogram(aplsalud_d, x = 'BMI',  nbins =20,
             width = 650, height = 500, title = '<b>Histograma de diabetes segun BMI <b>')

# agregar detalles
fig.update_layout(
    xaxis_title = '<b>Score<b>',
    yaxis_title = '<b>Frecuencia<b>',
    template = 'simple_white',
    title_x = 0.5,
    barmode='overlay')
fig.update_traces(opacity=0.75)

fig.show()

# Analisis de variables relacionadas con otras enfermedades

features = [ 'HighChol','Stroke', 'HighBP']
plt.figure(figsize = (30,23))
plt.suptitle('Diabetes by categorical features')

#subplots
for i in enumerate(features):
    plt.subplot(4,4, i[0]+1)   
    x = sns.countplot(data=aplsalud_d, x=i[1], hue='Diabetes', palette = ['deepskyblue','crimson'])
    for z in x.patches:
      x.annotate('{:.1f}'.format((z.get_height()/aplsalud_d.shape[0])*100)+'%',(z.get_x()+0.25, z.get_height()+0.01))

# Analisis de variables relacionados con habitos 

features = [ 'Smoker', 'PhysActivity', 'Fruits', 'Veggies', 'HvyAlcoholConsump', 'DiffWalk']
plt.figure(figsize = (30,23))
plt.suptitle('Diabetes by categorical features')

#subplots
for i in enumerate(features):
    plt.subplot(3,3, i[0]+1)   
    x = sns.countplot(data=aplsalud, x=i[1], hue='Diabetes', palette = ['deepskyblue','crimson'])
    for z in x.patches:
      x.annotate('{:.1f}'.format((z.get_height()/aplsalud.shape[0])*100)+'%',(z.get_x()+0.25, z.get_height()+0.01))

"""## **Feature selection**"""

aplsalud2

# Separacion de datos  
y=aplsalud2['Diabetes']
X= aplsalud2.loc[:, ~aplsalud2.columns.isin(['Diabetes'])]

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from numpy import set_printoptions

#crear un modelo de selección
est_prueba = SelectKBest(score_func=f_classif, k=9)
est_ajustado1 = est_prueba.fit(X, y)

#Muestro el desempeño de los features basado en el valoir F
set_printoptions(precision=5)
print(est_ajustado1.scores_)
features = est_ajustado1.transform(X)
print(features)
print(est_ajustado1.get_feature_names_out())
var_finales = est_ajustado1.get_feature_names_out()

# matriz con variables seleccionadas
X2=X[var_finales]

"""## **Algoritmos**"""

# importar 
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.tree import DecisionTreeClassifier  
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn import metrics
from sklearn.datasets import make_classification
from sklearn.ensemble import GradientBoostingClassifier

# Splitting the dataset into training and test set.  
X_train, X_test, Y_train, Y_test= train_test_split(X2, y, test_size= 0.33, random_state=0)

"""### **Gradient boosting classifier**"""

# Inicializar el clasificador de Gradient 

clf = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)

# Entrenar el clasificador con los datos de entrenamiento 

clf.fit(X_train, Y_train)

# Predecir las etiquetas de clase para los datos de prueba
y_pred = clf.predict(X_test) 

# Evaluar la precisión del modelo 

accuracy = accuracy_score(Y_test, y_pred) 
print("Precisión: {:.2f}".format(accuracy))

kfld = KFold(n_splits=10, random_state=6, shuffle=True)

res = cross_val_score(clf, X, y, cv=kfld)

res.mean()*100

#classification report
clf.fit(X_train, Y_train)
prediccion = clf.predict(X_test)
reporte = classification_report(Y_test,prediccion)
print(reporte)

#Creacion matriz de confusion 
cm= confusion_matrix(Y_test, y_pred) 
cm

"""###**Red neuronal profunda**"""

import keras #to Neural Network
from tensorflow.keras.utils import to_categorical #to classifcation neural network
from keras.models import Sequential #to define layers
from keras.layers import Dense #to define full conected layers
import matplotlib.pyplot as plt #to plot

# Splitting the dataset into training and test set.  
X_train, X_test, Y_train, Y_test= train_test_split(X2, y, test_size= 0.33, random_state=0)

from keras.models import Sequential
from keras.layers import Dense
import numpy as np

# definir el modelo
model = Sequential()
model.add(Dense(256, input_dim=9, activation='relu'))
model.add(Dense(128, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(16, activation='relu'))
model.add(Dense(8, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# compilar el modelo
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy','AUC', 'Recall', 'Precision'])

# entrenar el modelo
model.fit(X_train, Y_train, epochs=10, batch_size=100, validation_data=(X_test, Y_test))

#########Evaluar el modelo ####################
test_loss, test_acc, test_auc, test_recall, test_precision = model.evaluate(X_test, Y_test, verbose=2)
print("Test recall:", test_recall)

###### matriz de confusión test
pred_test=(model.predict(X_test) > 0.50).astype('int')

cm=metrics.confusion_matrix(Y_test,pred_test, labels=[1,0])
disp=metrics.ConfusionMatrixDisplay(cm,display_labels=['Diabetes', 'Normal'])
disp.plot()

print(metrics.classification_report(Y_test, pred_test))

# Aumento de capas y neuronas
model2 = Sequential()
model2.add(Dense(1024, input_dim=9, activation='relu'))
model2.add(Dense(512, activation='relu'))
model2.add(Dense(256, activation='relu'))
model2.add(Dense(128, activation='relu'))
model2.add(Dense(64, activation='relu'))
model2.add(Dense(64, activation='relu'))
model2.add(Dense(32, activation='relu'))
model2.add(Dense(16, activation='relu'))
model2.add(Dense(8, activation='relu'))
model2.add(Dense(1, activation='sigmoid'))

# compilar el modelo
model2.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy','AUC', 'Recall', 'Precision'])

# entrenar el modelo
model2.fit(X_train, Y_train, epochs=10, batch_size=50, validation_data=(X_test, Y_test))

#########Evaluar el modelo ####################
test_loss, test_acc, test_auc, test_recall, test_precision = model2.evaluate(X_test, Y_test, verbose=2)
print("Test auc:", test_recall)

# Aumento de epochs
model3 = Sequential()
model3.add(Dense(1024, input_dim=9, activation='relu'))
model3.add(Dense(512, activation='relu'))
model3.add(Dense(256, activation='relu'))
model3.add(Dense(128, activation='relu'))
model3.add(Dense(64, activation='relu'))
model3.add(Dense(64, activation='relu'))
model3.add(Dense(32, activation='relu'))
model3.add(Dense(16, activation='relu'))
model3.add(Dense(8, activation='relu'))
model3.add(Dense(1, activation='sigmoid'))

# compilar el modelo
model3.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy','AUC', 'Recall', 'Precision'])

# entrenar el modelo
model3.fit(X_train, Y_train, epochs=30, batch_size=100, validation_data=(X_test, Y_test))

#########Evaluar el modelo ####################
test_loss, test_acc, test_auc, test_recall, test_precision = model3.evaluate(X_test, Y_test, verbose=2)
print("Test auc:", test_recall)

# Función de activación tanh
model4 = Sequential()
model4.add(Dense(1024, input_dim=9, activation='tanh'))
model4.add(Dense(512, activation='tanh'))
model4.add(Dense(256, activation='tanh'))
model4.add(Dense(128, activation='tanh'))
model4.add(Dense(64, activation='tanh'))
model4.add(Dense(64, activation='tanh'))
model4.add(Dense(32, activation='tanh'))
model4.add(Dense(16, activation='tanh'))
model4.add(Dense(8, activation='tanh'))
model4.add(Dense(1, activation='sigmoid'))

# compilar el modelo
model4.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy','AUC', 'Recall', 'Precision'])

# entrenar el modelo
model4.fit(X_train, Y_train, epochs=10, batch_size=100, validation_data=(X_test, Y_test))

#########Evaluar el modelo ####################
test_loss, test_acc, test_auc, test_recall, test_precision = model4.evaluate(X_test, Y_test, verbose=2)
print("Test auc:", test_recall)

# Aumento de neuronas
model5 = Sequential()
model5.add(Dense(2048, input_dim=9, activation='relu'))
model5.add(Dense(1024, activation='relu'))
model5.add(Dense(1024, activation='relu'))
model5.add(Dense(512, activation='relu'))
model5.add(Dense(256, activation='relu'))
model5.add(Dense(128, activation='relu'))
model5.add(Dense(64, activation='relu'))
model5.add(Dense(32, activation='relu'))
model5.add(Dense(16, activation='relu'))
model5.add(Dense(8, activation='relu'))
model5.add(Dense(1, activation='sigmoid'))

# compilar el modelo
model5.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy','AUC', 'Recall', 'Precision'])

# entrenar el modelo
model5.fit(X_train, Y_train, epochs=10, batch_size=100, validation_data=(X_test, Y_test))

#########Evaluar el modelo ####################
test_loss, test_acc, test_auc, test_recall, test_precision = model5.evaluate(X_test, Y_test, verbose=2)
print("Test auc:", test_recall)

# Splitting the dataset into training and test set.  
X_train, X_test, Y_train, Y_test= train_test_split(X2, y, test_size= 0.20, random_state=0)

# Cambio de partición
model6 = Sequential()
model6.add(Dense(1024, input_dim=9, activation='relu'))
model6.add(Dense(512, activation='relu'))
model6.add(Dense(256, activation='relu'))
model6.add(Dense(128, activation='relu'))
model6.add(Dense(64, activation='relu'))
model6.add(Dense(64, activation='relu'))
model6.add(Dense(32, activation='relu'))
model6.add(Dense(16, activation='relu'))
model6.add(Dense(8, activation='relu'))
model6.add(Dense(1, activation='sigmoid'))

# compilar el modelo
model6.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy','AUC', 'Recall', 'Precision'])

# entrenar el modelo
model6.fit(X_train, Y_train, epochs=10, batch_size=100, validation_data=(X_test, Y_test))

#########Evaluar el modelo ####################
test_loss, test_acc, test_auc, test_recall, test_precision = model6.evaluate(X_test, Y_test, verbose=2)
print("Recall:", test_recall)

"""### **Red neuronal convolucional**"""

import tensorflow as tf
from sklearn import metrics

# Formatear los datos para el modelo
#X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
#X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

# Crear el modelo de red neuronal convolucional
model = tf.keras.Sequential([
    tf.keras.layers.Conv1D(32, 3, activation='relu', input_shape=(9, 1)),
    tf.keras.layers.Conv1D(64, 3, activation='relu'),
    tf.keras.layers.Conv1D(128, 3, activation='relu'),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# Compile the model with binary cross-entropy loss and Adam optimizer
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['Recall'])

# Train the model for 10 epochs
model.fit(X_train, Y_train, batch_size=100, epochs=10, validation_data=(X_test, Y_test))

!pip install keras-tuner

import keras_tuner as kt

def build_model(hp):
   
    optimizer = hp.Choice('optimizer', ['adam', 'sgd', 'rmsprop'])
    if optimizer == 'adam':
        opt = tf.keras.optimizers.Adam(learning_rate=0.001)
    elif optimizer == 'sgd':
        opt = tf.keras.optimizers.SGD(learning_rate=0.01)
    else:
        opt = tf.keras.optimizers.RMSprop(learning_rate=0.0001)
   
    model.compile(
        optimizer=opt, loss="binary_crossentropy", metrics=["Recall"],
    )
    return model

hp = kt.HyperParameters()
build_model(hp)

tuner = kt.RandomSearch(
    hypermodel=build_model,
    hyperparameters=hp,
    tune_new_entries=False, ## solo evalúe los hiperparámetros configurados
    objective=kt.Objective("val_recall", direction="max"),
    max_trials=10,
    overwrite=True, 
)

tuner.search(X_train, Y_train, epochs=5, validation_data=(X_test, Y_test), batch_size=100)

fc_best_model = tuner.get_best_models(num_models=1)[0]
tuner.results_summary()

###### matriz de confusión test
pred_test=(fc_best_model.predict(X_test) > 0.50).astype('int')

cm=metrics.confusion_matrix(Y_test,pred_test, labels=[1,0])
disp=metrics.ConfusionMatrixDisplay(cm,display_labels=['Diabetes', 'Normal'])
disp.plot()

print(metrics.classification_report(Y_test, pred_test))