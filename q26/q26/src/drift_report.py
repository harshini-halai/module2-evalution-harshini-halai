import json
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp


train = pd.read_csv("data/train.csv")
production = pd.read_csv("data/production_sample.csv")


numeric_columns = [
    "age",
    "annual_income",
    "employment_years",
    "credit_score",
    "loan_amount"
]


report = {}


for column in numeric_columns:

    train_values = train[column]
    production_values = production[column]

    # KS test
    ks_stat, p_value = ks_2samp(
        train_values,
        production_values
    )

    # PSI
    bins = np.linspace(
        min(train_values.min(), production_values.min()),
        max(train_values.max(), production_values.max()),
        11
    )

    train_counts = np.histogram(train_values, bins=bins)[0]
    production_counts = np.histogram(production_values, bins=bins)[0]

    train_percent = train_counts / len(train_values)
    production_percent = production_counts / len(production_values)

    train_percent = np.where(train_percent == 0, 0.0001, train_percent)
    production_percent = np.where(production_percent == 0, 0.0001, production_percent)

    psi = np.sum(
        (production_percent - train_percent)
        * np.log(production_percent / train_percent)
    )

    if psi < 0.1:
        psi_band = "no significant drift"
    elif psi <= 0.25:
        psi_band = "moderate drift"
    else:
        psi_band = "significant drift"

    report[column] = {
        "ks_statistic": float(ks_stat),
        "ks_p_value": float(p_value),
        "ks_drift": bool(p_value < 0.05),
        "psi": float(psi),
        "psi_band": psi_band
    }


# Demographic parity
group_rates = {}

for group in ["A", "B"]:

    group_data = production[
        production["applicant_group"] == group
    ]

    if len(group_data) > 0:
        group_rates[group] = float(
            group_data["approved"].mean()
        )

if "A" in group_rates and "B" in group_rates:

    demographic_parity_difference = abs(
        group_rates["A"] - group_rates["B"]
    )

else:
    demographic_parity_difference = None


report["demographic_parity"] = {
    "positive_rate_A": group_rates.get("A"),
    "positive_rate_B": group_rates.get("B"),
    "difference": demographic_parity_difference
}


with open("metrics/drift_report.json", "w") as file:
    json.dump(report, file, indent=2)


print("Drift report created")