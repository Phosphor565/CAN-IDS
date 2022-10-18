'''
This script tests the implementation of the Gaussian Naive Bayes
machine learning algorithm and outputs statistsics on the effectiveness
of said algorithms

Author: Phosphor565
Date: 10/5/22

https://scikit-learn.org/stable/index.html
'''
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score

# Import Dataset
names = ['Interval','Frequency', 'Classifiaction']
CAN_dataset = pd.read_csv("CAN_data.csv")

# Data processing
X = CAN_dataset.iloc[:,0:2].values
y = CAN_dataset.iloc[:, 2].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=7, shuffle=True)

# GNB Implementation
nb = GaussianNB()
nb.fit(X_train, y_train)
y_pred = nb.predict(X_test)

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
plt.title("NB Confusion Matrix")
plt.show()