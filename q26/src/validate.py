import sys
import pandas as pd

if len(sys.argv) != 2:
    raise SystemExit("Usage: python validate.py <train.csv> <bad.csv> <production.csv>")

df_train = pd.read_csv(sys.argv[1])
df_bad = pd.read_csv(sys.argv[2])
df_production = pd.read_csv(sys.argv[3])

expected_columns = [
    "applicant_id",
    "age",
    "annual_income",
    "employment_years",
    "credit_score",
    "loan_amount",
    "applicant_group",
    "region",
    "approved"
]
actual_train_columns = df_train.columns.tolist()
actual_bad_columns = df_bad.columns.tolist()
actual_production_columns = df_production.columns.tolist()

if actual_train_columns == expected_columns:
    print("Train schema is valid")
else:
    print("Train schema is invalid")

if actual_bad_columns == expected_columns:
    print("Bad schema is valid")
else:
    print("Bad schema is invalid")

if actual_production_columns == expected_columns:
    print("Production schema is valid")
else:
    print("Production schema is invalid")