import pandas as pd


df = pd.read_csv("data/loan_application.csv")

df = df.drop_duplicates()

df.to_csv("data/train.csv", index=False)

print("Training data prepared")
print("Rows:", len(df))