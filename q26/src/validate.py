import sys
import pandas as pd
import json
import os

file_path = sys.argv[1]

df = pd.read_csv(file_path)

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

errors = []


# Check columns
if list(df.columns) != expected_columns:
    errors.append("Schema mismatch")


# Check numeric columns
numeric_columns = [
    "applicant_id",
    "age",
    "annual_income",
    "employment_years",
    "credit_score",
    "loan_amount",
    "approved"
]

# column is numeric or not
for column in numeric_columns:
    if not pd.api.types.is_numeric_dtype(df[column]):
        errors.append(column + " must be numeric")


# missing values
if df.isnull().any().any():
    errors.append("Null values found")


# Check ranges
if not df["age"].between(21, 70).all():
    errors.append("Age must be between 21 and 70")

if not df["credit_score"].between(300, 900).all():
    errors.append("Credit score must be between 300 and 900")

if not df["employment_years"].between(0, 35).all():
    errors.append("Employment years must be between 0 and 35")

if (df["annual_income"] < 0).any():
    errors.append("Annual income cannot be negative")

if (df["loan_amount"] < 0).any():
    errors.append("Loan amount cannot be negative")


# Check categories
if not df["applicant_group"].isin(["A", "B"]).all():
    errors.append("Invalid applicant_group")

if not df["region"].isin(["north", "south", "east", "west"]).all():
    errors.append("Invalid region")


if errors:
    print("Validation FAILED")

    for error in errors:
        print("ERROR:", error)

    sys.exit(1)


print("Validation PASSED")
print("Rows checked:", len(df))

with open("metrics/validation_report.json", "w") as f:
    json.dump({"status": "PASSED"}, f)