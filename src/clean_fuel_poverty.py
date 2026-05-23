"""
clean_fuel_poverty.py
---------------------
Cleans sub-regional fuel poverty statistics (DESNZ, 2025 release)
to local authority level using the LILEE metric.

Input:  data/raw/fuel_poverty_2023.xlsx
Output: data/processed/fuel_poverty_by_la.csv
"""

import pandas as pd
import os

def load_fuel_poverty(filepath):
    """Load fuel poverty data from the government statistics workbook."""
    df = pd.read_excel(
        filepath,
        sheet_name='Table 3',
        skiprows=2,
        header=0
    )
    return df

def clean_fuel_poverty(df):
    """Select and rename relevant columns."""
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    # Retain local authority code, name, region, fuel poverty rate and count
    keep_cols = [c for c in df.columns if any(k in c for k in [
        'ons_code', 'local_authority', 'region', 'fuel_poor', 'proportion'
    ])]
    df = df[keep_cols].copy()
    df = df.dropna(subset=[c for c in df.columns if 'ons_code' in c or 'local_authority' in c][:1])
    # Standardise column names
    rename_map = {}
    for col in df.columns:
        if 'ons_code' in col:
            rename_map[col] = 'local_authority_code'
        elif 'local_authority' in col and 'name' not in rename_map.values():
            rename_map[col] = 'local_authority_name'
        elif 'region' in col and 'region' not in rename_map.values():
            rename_map[col] = 'region'
        elif 'proportion' in col or 'percent' in col:
            rename_map[col] = 'fuel_poverty_rate'
        elif 'fuel_poor' in col and 'households' not in rename_map.values():
            rename_map[col] = 'fuel_poor_households'
    df = df.rename(columns=rename_map)
    df['fuel_poverty_rate'] = pd.to_numeric(df.get('fuel_poverty_rate', pd.Series()), errors='coerce')
    df['fuel_poor_households'] = pd.to_numeric(df.get('fuel_poor_households', pd.Series()), errors='coerce')
    return df

def main():
    raw_path = os.path.join('data', 'raw', 'fuel_poverty_2023.xlsx')
    out_path = os.path.join('data', 'processed', 'fuel_poverty_by_la.csv')
    print(f"Loading fuel poverty data from {raw_path}...")
    df = load_fuel_poverty(raw_path)
    print(f"  Loaded {len(df)} rows")
    df = clean_fuel_poverty(df)
    print(f"  Cleaned: {len(df)} local authorities")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"  Saved to {out_path}")
    return df

if __name__ == '__main__':
    main()
