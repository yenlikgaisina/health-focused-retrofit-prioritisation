"""
clean_health.py
---------------
Extracts and cleans respiratory health indicators from OHID Fingertips
(Public Health England / UKHSA data) at local authority level.

Indicators used:
  - COPD: unplanned hospital admissions (rate per 100,000)
  - Asthma: emergency admissions (rate per 100,000)
  - Respiratory mortality rate

Input:  data/raw/respiratory_indicators.csv
Output: data/processed/respiratory_health_by_la.csv
"""

import pandas as pd
import os

INDICATOR_NAMES = {
    'copd': ['copd', 'chronic obstructive pulmonary'],
    'asthma': ['asthma'],
    'respiratory_mortality': ['respiratory mortality', 'respiratory disease: mortality']
}

def load_fingertips(filepath):
    """Load Fingertips indicator export CSV."""
    df = pd.read_csv(filepath, low_memory=False)
    return df

def clean_fingertips(df):
    """Filter to relevant indicators and local authority geography."""
    df = df.copy()
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    # Filter to local authority level
    la_mask = df['area_type'].str.lower().str.contains('district|county|unitary|local authority', na=False)
    df = df[la_mask].copy()

    # Assign indicator category
    def categorise(name):
        if not isinstance(name, str):
            return None
        n = name.lower()
        for cat, keywords in INDICATOR_NAMES.items():
            if any(k in n for k in keywords):
                return cat
        return None

    df['indicator_category'] = df['indicator_name'].apply(categorise)
    df = df.dropna(subset=['indicator_category'])

    # Keep most recent year per LA per indicator
    df['time_period_sortable'] = pd.to_numeric(
        df['time_period'].astype(str).str[:4], errors='coerce'
    )
    df = df.sort_values('time_period_sortable', ascending=False)
    df = df.drop_duplicates(subset=['area_code', 'indicator_category'], keep='first')

    # Pivot to wide format
    pivot = df.pivot_table(
        index=['area_code', 'area_name', 'parent_name'],
        columns='indicator_category',
        values='value',
        aggfunc='first'
    ).reset_index()

    pivot.columns.name = None
    pivot = pivot.rename(columns={
        'area_code': 'local_authority_code',
        'area_name': 'local_authority_name',
        'parent_name': 'region',
        'copd': 'copd_admission_rate',
        'asthma': 'asthma_admission_rate',
        'respiratory_mortality': 'respiratory_mortality_rate'
    })

    for col in ['copd_admission_rate', 'asthma_admission_rate', 'respiratory_mortality_rate']:
        if col not in pivot.columns:
            pivot[col] = float('nan')

    return pivot[[
        'local_authority_code', 'local_authority_name', 'region',
        'copd_admission_rate', 'asthma_admission_rate', 'respiratory_mortality_rate'
    ]]

def main():
    raw_path = os.path.join('data', 'raw', 'respiratory_indicators.csv')
    out_path = os.path.join('data', 'processed', 'respiratory_health_by_la.csv')
    print(f"Loading Fingertips data from {raw_path}...")
    df = load_fingertips(raw_path)
    print(f"  Loaded {len(df):,} rows")
    df = clean_fingertips(df)
    print(f"  Cleaned to {len(df)} local authorities")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"  Saved to {out_path}")
    return df

if __name__ == '__main__':
    main()
