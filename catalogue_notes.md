# Recent Solar-PV Datasets (2024–2026): systematic catalogue

**Search cut-off:** 16 August 2026  
**Deliverable:** [`solar_pv_datasets_2024_2026.csv`](solar_pv_datasets_2024_2026.csv)

## Important interpretation

The requested date window is applied to the **public dataset release or frozen annual update**, not necessarily to the dates when measurements were collected. A 2025 release can therefore contain measurements from 2021–2024. This is recorded separately in `Collection Period`.

The catalogue deliberately distinguishes:

- **Real** — directly measured field, plant, laboratory, UAV, or administrative records.
- **Derived** — real satellite/registry/weather inputs transformed into polygons, harmonized assets, or corrected profiles.
- **Mixed** — empirical inputs plus modelled/debiased variables.
- **Synthetic/simulated** — circuit, power-system, climate, or generative-model output.

`NR` means **not reported in the repository metadata inspected**, not zero and not unavailable. It is preferable to an invented value.

## Ranking method

Rows are grouped by the requested A–G categories and ranked within the primary category using a qualitative combination of:

1. direct relevance to PV cells/modules/systems/plants;
2. recency (2026 > 2025 > 2024);
3. access and licensing;
4. size and temporal/spatial coverage;
5. utility for ML, diagnosis, forecasting, degradation, or operations;
6. strength of verification (repository record + paper preferred).

The category-rank prefix is:

- `A`: EL
- `B`: RGB / visible / remote-sensing imagery
- `C`: thermal / infrared
- `D`: electrical and operational time series
- `E`: irradiance and environmental time series
- `F`: performance, planning, and lower-priority simulated data
- `G`: multimodal

## Highest-priority shortlist

### EL

1. **PV image database (visible, EL, IR) for LLM evaluation** — recent, openly licensed multimodal collection.
2. **elpv-dataset 1.0.0.post1** — small but exceptionally established EL benchmark; qualifying date is the 2024 release, not original acquisition.
3. **PVEL-AD** — large open anomaly benchmark; check repository release history when a strict first-publication date is required.

### RGB / geospatial imagery

1. **Labeled PV installations for Queens, New York** (2026).
2. **Global Photovoltaic Solar Panel Dataset 2019–2022** (released 2024; Scientific Data paper 2025).
3. **Solar Asset Mapper Q1 2024** — 63,616 assets in 183 countries.
4. **Global Renewables Watch** — 86,410 solar installations with temporal attributes.
5. **CPVPD-2024** and **ChinaPV-10m-2024** — national-scale Chinese vectors.
6. **Real-World UAV PV Soiling Dataset** — close-range/UAV field inspection rather than mapping.

### Thermal

1. **THED-PV** — 12,460 real 640×512 thermal images and 99,680 homography pairs.
2. **Thermal PV Panel Detection and Fault Detection Dataset for UAV-Based Inspection** — 353 frames and 26,678 panel annotations.
3. **PVMD** — 1,000 field UAV thermal/visible images across hotspot, crack, and shading classes.
4. **Experimental Data for Mismatching Faults** — unusually useful thermal + visible + electrical measurements.

### Electrical / operational

1. **Hong Kong high-resolution rooftop PV dataset** — 60 stations, 6,085 modules, three years, electrical and on-site weather data.
2. **PTProsumer** — 24 sites, one-second data, approximately 3.89 billion points.
3. **TRUST-PV Bolzano** — full-year bifacial HJT tracker measurements.
4. **DTU module-level IV curves** — bifacial module IV curves with front/rear irradiance and module temperature.
5. **IFES Serra** — real 3 kWp and 119 kWp Brazilian plant monitoring.
6. **LBNL Utility-Scale Solar 2025** — 1,760 projects; broad plant metadata and debiased hourly profiles.

### Environmental

1. **PV-Live** — real minute-resolution irradiance/reference-cell network.
2. **Time-series weather dataset for predicting PV energy in Portugal** — real weather-station observations.
3. **NSRDB 2024 annual update** — foundational satellite/reanalysis resource; not direct plant telemetry.
4. **U.S. Agrivoltaics Irradiance Database** — very large, but modelled from NSRDB/SAM.

## Caveats and quality controls

- **Do not infer “real” from a realistic-looking title.** The CSV marks simulation, satellite-derived, and mixed products explicitly.
- A DOI in `DOI` can be the dataset DOI or associated article DOI, as requested. The `Associated Paper` field distinguishes the latter where known.
- Image resolution and sample count are left `NR` unless explicit repository/paper metadata was found.
- Roboflow/Kaggle and project-web datasets are lower-ranked because provenance, stable versioning, or registration can be weaker than Zenodo, Dryad, Mendeley, OEDI, and institutional Figshare.
- Remote-sensing PV footprint datasets describe real installations but are **derived observations**, not module-condition images.
- Annual editions (for example LBNL Utility-Scale Solar 2024 and 2025) are retained as distinct frozen research products. Living databases are not multiplied by every access date; only one qualifying update is catalogued per living product.
- Several 2026 records are very recent. Check their repository landing page for corrected versions before freezing a research benchmark.

## Reproducible audit checks

Before selecting a dataset for a paper:

1. open the repository landing page;
2. confirm release date/version and license;
3. inspect the README/data dictionary;
4. download one representative file;
5. verify units, timestamp timezone, missing-data encoding, and train/test leakage risk;
6. cite both dataset DOI and associated paper DOI where they differ.
