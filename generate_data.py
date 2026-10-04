"""
Optional helper: the bootcamp allows synthetic data.
The included CSV is already ready to use. This script simply validates
that the dataset is readable and reports its basic statistics.
"""

import pandas as pd

df = pd.read_csv("data/recipes.csv")

print("Rows:", len(df))
print("Columns:", list(df.columns))
print("\nCuisine counts:")
print(df["cuisine"].value_counts())

print("\nAverage cooking time:",
      round(df["cooking_time_minutes"].mean(), 2), "minutes")
