# Health-Focused Retrofit Prioritisation in England

**Linking housing energy efficiency, fuel poverty and respiratory health outcomes**

## Project question

Which local authorities in England should be prioritised for retrofit investment because they combine poor housing energy efficiency, fuel poverty and worse respiratory health outcomes?

## Why this matters

Buildings are not only an environmental issue. They are also a public health issue. Poorly insulated homes can contribute to cold, damp and unaffordable living conditions, while retrofit can support both net zero goals and health equity.

This project connects construction sustainability to public health by identifying local authorities where housing energy inefficiency, fuel poverty and respiratory health risk overlap — areas where retrofit investment could deliver both environmental and health benefits.

## Data sources

| Dataset | Source | What it provides |
|---------|--------|-----------------|
| EPC Open Data | MHCLG / EPC Register | Housing energy efficiency by property |
| Sub-regional Fuel Poverty Statistics | DESNZ (2025 release) | Fuel poverty rate by local authority (LILEE metric) |
| OHID Fingertips Respiratory Profile | UKHSA / OHID | COPD admissions, asthma admissions, respiratory mortality |
| ONS Green Space Access | ONS | Access to gardens and public green space (v2 addition) |

### Data tracking

| Data source | File name | Downloaded? | Notes |
|-------------|-----------|-------------|-------|
| EPC Open Data | epc_domestic.csv | No | Use local authority and energy rating fields |
| Fuel Poverty | fuel_poverty_2023.xlsx | No | Use local authority table (LILEE metric) |
| OHID Fingertips | respiratory_indicators.csv | No | Use COPD/asthma/respiratory mortality indicators |
| ONS Green Space | green_space_access.csv | No | Optional for version 1 |

## Method

1. Aggregate housing energy efficiency indicators by local authority from EPC open data
2. Join sub-regional fuel poverty statistics (LILEE metric, 2023)
3. Join respiratory health indicators from OHID Fingertips
4. Calculate a composite retrofit-health priority score
5. Rank local authorities by combined sustainability and public health need
6. Assign priority bands: Very High / High / Medium / Low

### Priority score formula

```
retrofit_health_priority_score =
  0.4 × normalised_percent_homes_below_epc_c
+ 0.3 × normalised_fuel_poverty_rate
+ 0.3 × normalised_respiratory_health_risk
```

### Priority bands

| Band | Percentile threshold |
|------|----------------------|
| Very High | Top 20% |
| High | Next 20% (60th–80th percentile) |
| Medium | Middle 40% (20th–60th percentile) |
| Low | Bottom 20% |

## Outputs

- `data/output/health_focused_retrofit_prioritisation_england.csv` — combined dataset with priority scores
- Priority scoring table and ranked local authorities
- 5 visualisations (see `visuals/` and Colab notebook)
- Top 20 priority local authorities

### Visualisations

1. **Top 20 local authorities for health-focused retrofit** — bar chart
2. **Housing inefficiency vs fuel poverty** — scatter plot
3. **Fuel poverty vs respiratory health outcomes** — scatter plot
4. **Retrofit-health priority matrix** — bubble chart
5. **Priority band distribution** — bar chart

## Project structure

```
health-focused-retrofit-prioritisation/
  README.md
  requirements.txt
  data/
    raw/          ← place downloaded source files here
    processed/    ← cleaned intermediate files
    output/       ← final combined CSV
  notebooks/
    health_focused_retrofit_analysis.ipynb
  visuals/        ← exported chart images
  src/
    clean_epc.py
    clean_fuel_poverty.py
    clean_health.py
    build_dataset.py
```

## How to run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place raw data files in data/raw/

# 3. Clean each source
python src/clean_epc.py
python src/clean_fuel_poverty.py
python src/clean_health.py

# 4. Build the combined dataset
python src/build_dataset.py

# 5. Run the Colab notebook for visualisations
# Open notebooks/health_focused_retrofit_analysis.ipynb in Google Colab
```

## Limitations

This project identifies overlapping risk patterns. It does **not** prove causation between housing energy efficiency and respiratory health outcomes.

Areas flagged as high priority reflect a co-occurrence of housing, economic and health risk indicators. They are signals for further investigation and intervention planning, not direct evidence of a causal link.

Language used in this project: *overlap*, *association*, *priority signal*, *areas for further investigation*.

## Skills demonstrated

Python · pandas · public health analytics · retrofit · EPC data · fuel poverty · respiratory health · sustainability · data visualisation

---

*Part of the Gaisina Consulting Group portfolio. Separate from the ESG Construction Sustainability Media Analysis project.*
