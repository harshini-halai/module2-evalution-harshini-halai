import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import yaml

with open("params.yaml", "r") as f:
    params = yaml.safe_load(f)

df = pd.read_csv("data/train.csv")

X = df.drop(columns=["approved"])
y = df["approved"]

X = pd.get_dummies(X)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=params["model"]["n_estimators"],
    random_state=params["model"]["random_state"]
)

model.fit(X_train, y_train)

with open("models/model.pkl", "wb") as file:
    pickle.dump(model, file)

print("Model trained")