'''
This script tests the implementation of the K-Nearest Neighbour
machine learning algorithm and outputs statistsics on the effectiveness
of said algorithms

Author: Phosphor565
Date: 10/5/22

https://scikit-learn.org/stable/index.html
'''
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# Import Dataset
names = ['Interval','Frequency', 'Classifiaction']
CAN_dataset = pd.read_csv("CAN_data.csv")

# Data processing
X = CAN_dataset.iloc[:,0:2].values
y = CAN_dataset.iloc[:, 2].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=7, shuffle=True)

# KNN Implementation
classifier = KNeighborsClassifier(n_neighbors=5)
classifier.fit(X_train, y_train)
y_pred = classifier.predict(X_test)

# Evaluating Performance
print("Confusion Matrix")
print(confusion_matrix(y_test, y_pred))
print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
print("\nClassification Report")
print("__________________________________________________________")
print(classification_report(y_test, y_pred))
print("__________________________________________________________")
print('\nAccuracy - ' + str(accuracy_score(y_test, y_pred)))
print("\nDisplaying graphical Confusion Matrix")
ConfusionMatrixDisplay.from_predictions(y_test, y_pred)
plt.title("KNN Confusion Matrix")
plt.show()