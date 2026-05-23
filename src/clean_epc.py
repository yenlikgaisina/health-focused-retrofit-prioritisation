"""
clean_epc.py
Cleans and aggregates EPC (Energy Performance Certificate) open data
from the MHCLG EPC register to local authority level.
Input:  data/raw/epc_domestic.csv
Output: data/processed/epc_by_la.csv
"""

import pandas as pd
import numpy as np
import os

EPC_RATING_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7}

def load_epc(filepath):
    cols = [
        'LOCAL_AUTHORITY', 'LOCAL_AUTHORITY_LABEL',
        'CURRENT_ENERGY_RATING', 'CURRENT_ENERGY_EFFICIENCY',
        'CO2_EMISSIONS_CURRENT', 'REGION'
    ]
    df = pd.read_csv(filepath, usecols=cols, low_memory=False)
    return df

def clean_epc(df):
    df = df.copy()
    df.columns = df.columns.str.lower()
    df = df.dropna(subset=['local_authority', 'current_energy_rating'])
    df['current_energy_rating'] = df['current_energy_rating'].str.upper().str.strip()
    df = df[df['current_energy_rating'].isin(EPC_RATING_MAP.keys())]
    df['epc_numeric'] = df['current_energy_rating'].map(EPC_RATING_MAP)
    df['is_c_or_above'] = df['current_energy_rating'].isin(['A', 'B', 'C']).astype(int)
    df['current_energy_efficiency'] = pd.to_numeric(df['current_energy_efficiency'], errors='coerce')
    df['co2_emissions_current'] = pd.to_numeric(df['co2_emissions_current'], errors='coerce')
    return df

def aggregate_by_la(df):
    agg = df.groupby(['local_authority', 'local_authority_label', 'region']).agg(
        total_properties=('epc_numeric', 'count'),
        avg_epc_score=('current_energy_efficiency', 'mean'),
        avg_co2_emissions_per_property=('co2_emissions_current', 'mean'),
        homes_c_or_above=('is_c_or_above', 'sum'),
    ).reset_index()
    agg['percent_homes_epc_c_or_above'] = (agg['homes_c_or_above'] / agg['total_properties'] * 100).round(2)
    agg['percent_homes_below_epc_c'] = (100 - agg['percent_homes_epc_c_or_above']).round(2)
    agg = agg.rename(columns={
        'local_authority': 'local_authority_code',
        'local_authority_label': 'local_authority_name'
    })
    return agg[['local_authority_code', 'local_authority_name', 'region',
        'avg_epc_score', 'percent_homes_epc_c_or_above', 'percent_homes_below_epc_c',
        'avg_co2_emissions_per_property']]

def main():
    raw_path = os.path.join('data', 'raw', 'epc_domestic.csv')
    out_path = os.path.join('data', 'processed', 'epc_by_la.csv')
    print(f"Loading EPC data from {raw_path}...")
    df = load_epc(raw_path)
    print(f"  Loaded {len(df):,} records")
    df = clean_epc(df)
    print(f"  After cleaning: {len(df):,} records")
    agg = aggregate_by_la(df)
    print(f"  Aggregated to {len(agg)} local authorities")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    agg.to_csv(out_path, index=False)
    print(f"  Saved to {out_path}")
    return agg

if __name__ == '__main__':
    main()
