# Q26 Notes

## Project

Q26 is an offline 20-mark lender-model audit project.

The project is designed to validate loan application data, build a reproducible ML pipeline, evaluate the model, and monitor production data drift.

## Important Constraints

- No API key
- No Docker
- No internet/network dependency
- Local folder is used as the DVC remote
- Data is tracked with DVC, not Git

## Data Files

The following three CSV files are tracked with DVC:

- loan_applications.csv
- loan_applications_bad.csv
- production_sample.csv

The bad CSV is intentionally used to verify that validation catches invalid data and stops the pipeline before training.

## Validation

The validator checks:

- Exact required schema
- No extra columns
- Numeric data types
- Null values
- Age range: 21–70
- Credit score range: 300–900
- Employment years range: 0–35
- No negative monetary values
- applicant_group categories: A / B
- region categories: north / south / east / west

The validator reports all detected defects instead of stopping at the first defect.

Invalid CSV data must cause the validation command to exit with a non-zero status.

## DVC Pipeline

The main pipeline stages are:

1. validate
2. prepare
3. train
4. evaluate

A separate drift analysis is also included.

The pipeline ensures that bad data is rejected before model training.

## DVC

DVC is used to version the large/data files while Git tracks the code and pipeline metadata.

Important DVC files include:

- .dvc
- dvc.yaml
- dvc.lock
- .dvcignore

The local folder is configured as the DVC remote.

## Drift Detection

The drift report is written to:

metrics/drift_report.json

Training data is compared against:

production_sample.csv

For every numeric feature, the Kolmogorov-Smirnov (KS) test is calculated.

A feature is flagged for KS drift when:

p < 0.05

Population Stability Index (PSI) is calculated using hand-coded PSI bands.

Demographic parity difference is also checked.

The demographic-parity calculation handles cases where a demographic group is absent instead of crashing.

Not every feature is expected to be drifted.

## Reproducibility

Changing parameters should allow the DVC pipeline to rerun only the affected stages.

Unchanged stages can be skipped when their dependencies and outputs are still valid.

The project should also demonstrate how to restore an earlier model and its metrics using DVC.

## Lineage

The project documents the lineage:

data hash
→ parameters
→ code commit
→ model
→ metrics

This makes it possible to understand which data, parameters and code produced a particular model and evaluation result.

## Main Goal

The final system demonstrates that a lender ML workflow can:

- reject invalid data
- reproduce model training
- track data versions
- evaluate the model
- detect production drift
- maintain traceability from data to model and metrics