import pandas as pd
import pickle
from sklearn.metrics import accuracy_score


df = pd.read_csv("data/train.csv")

X = df.drop(columns=["approved"])
y = df["approved"]

X = pd.get_dummies(X)

with open("models/model.pkl", "rb") as file:
    model = pickle.load(file)

predictions = model.predict(X)

accuracy = accuracy_score(y, predictions)

print("Accuracy:", accuracy)