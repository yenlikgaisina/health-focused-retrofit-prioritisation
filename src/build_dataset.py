"""
build_dataset.py
----------------
Merges cleaned EPC, fuel poverty and respiratory health data.
Calculates the retrofit-health priority score and assigns priority bands.

Output: data/output/health_focused_retrofit_prioritisation_england.csv

Priority score formula:
  retrofit_health_priority_score =
    0.4 * normalised_percent_homes_below_epc_c
  + 0.3 * normalised_fuel_poverty_rate
  + 0.3 * normalised_respiratory_health_risk

Priority bands:
  Top 20%  = Very High
  Next 20% = High
  Middle 40% = Medium
  Bottom 20% = Low

IMPORTANT: This analysis identifies overlapping risk patterns.
It does not prove causation between housing quality and health outcomes.
"""

import pandas as pd
import numpy as np
import os

def normalise(series):
    """Min-max normalise a pandas Series to [0, 1]."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.5, index=series.index)
    return (series - mn) / (mx - mn)

def assign_priority_band(score_series):
    """Assign priority band based on score percentile."""
    p20 = score_series.quantile(0.20)
    p40 = score_series.quantile(0.40)
    p80 = score_series.quantile(0.80)

    def band(s):
        if s >= p80:
            return 'Very High'
        elif s >= p40:
            return 'High'
        elif s >= p20:
            return 'Medium'
        else:
            return 'Low'

    return score_series.apply(band)

def build(epc_path, fp_path, health_path, output_path):
    print("Loading cleaned data sources...")
    epc = pd.read_csv(epc_path)
    fp = pd.read_csv(fp_path)
    health = pd.read_csv(health_path)

    print(f"  EPC: {len(epc)} LAs | Fuel poverty: {len(fp)} LAs | Health: {len(health)} LAs")

    # Merge on local_authority_code
    df = epc.merge(
        fp[['local_authority_code', 'fuel_poverty_rate', 'fuel_poor_households']],
        on='local_authority_code', how='left'
    )
    df = df.merge(
        health[['local_authority_code', 'copd_admission_rate',
                'asthma_admission_rate', 'respiratory_mortality_rate']],
        on='local_authority_code', how='left'
    )

    # Composite respiratory health risk (mean of available indicators)
    resp_cols = ['copd_admission_rate', 'asthma_admission_rate', 'respiratory_mortality_rate']
    df['respiratory_health_risk'] = df[resp_cols].mean(axis=1)

    # Normalise inputs
    df['norm_epc'] = normalise(df['percent_homes_below_epc_c'].fillna(df['percent_homes_below_epc_c'].median()))
    df['norm_fp'] = normalise(df['fuel_poverty_rate'].fillna(df['fuel_poverty_rate'].median()))
    df['norm_health'] = normalise(df['respiratory_health_risk'].fillna(df['respiratory_health_risk'].median()))

    # Priority score
    df['retrofit_health_priority_score'] = (
        0.4 * df['norm_epc'] +
        0.3 * df['norm_fp'] +
        0.3 * df['norm_health']
    ).round(4)

    # Priority band
    df['priority_band'] = assign_priority_band(df['retrofit_health_priority_score'])

    # Add retrofit_need_score (EPC-only component)
    df['retrofit_need_score'] = normalise(df['percent_homes_below_epc_c'].fillna(0)).round(4)

    # Green space placeholder (to be populated in v2)
    df['green_space_access_score'] = float('nan')

    # Select and order final columns
    final_cols = [
        'local_authority_code', 'local_authority_name', 'region',
        'avg_epc_score', 'percent_homes_epc_c_or_above', 'percent_homes_below_epc_c',
        'avg_co2_emissions_per_property', 'retrofit_need_score',
        'fuel_poverty_rate', 'fuel_poor_households',
        'copd_admission_rate', 'asthma_admission_rate', 'respiratory_mortality_rate',
        'green_space_access_score',
        'retrofit_health_priority_score', 'priority_band'
    ]
    df = df[[c for c in final_cols if c in df.columns]]
    df = df.sort_values('retrofit_health_priority_score', ascending=False).reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"  Output saved: {output_path}")
    print(f"  Total LAs: {len(df)}")
    print("\nPriority band distribution:")
    print(df['priority_band'].value_counts())
    return df

def main():
    epc_path = os.path.join('data', 'processed', 'epc_by_la.csv')
    fp_path = os.path.join('data', 'processed', 'fuel_poverty_by_la.csv')
    health_path = os.path.join('data', 'processed', 'respiratory_health_by_la.csv')
    output_path = os.path.join('data', 'output', 'health_focused_retrofit_prioritisation_england.csv')
    return build(epc_path, fp_path, health_path, output_path)

if __name__ == '__main__':
    main()
