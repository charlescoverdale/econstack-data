# econstack-data

Data and parameters for [econstack](https://github.com/charlescoverdale/econstack). Three types of data: regional economic profiles, IO multipliers, and appraisal parameter files.

## Installation

```bash
git clone https://github.com/charlescoverdale/econstack-data.git ~/econstack-data
```

Then install [econstack](https://github.com/charlescoverdale/econstack) to use the data.

## Contents

### UK Local Authority Data (`src/data/`)

Pre-processed economic data for 391 UK local authorities. Each LA has up to 16 JSON files:

| Dataset | Source |
|---|---|
| Employment by sector (19 SIC sections) | BRES via Nomis |
| Earnings (percentiles p10-p90, gender gap) | ASHE via Nomis |
| IO multipliers (output + employment, Type I + II) | ONS IOAT 2023 + FLQ |
| Population (mid-year estimates, age profile) | ONS |
| Housing (prices, affordability, tenure) | DLUHC / HM Land Registry |
| GVA by industry | ONS (estimated from national ratios) |
| Business counts (size bands) | ONS UK Business Counts |
| Business demography (births, deaths, survival) | ONS |
| Deprivation (IMD, 7 domains) | MHCLG (England only) |
| Skills (occupations, qualifications) | Census 2021 via Nomis |
| Commuting (modes, WFH %) | Census 2021 via Nomis |
| National benchmarks | Aggregated from above |

### Australian IO Data (`src/data/au/`)

Regional input-output multipliers for 88 Australian SA4 regions, built from ABS IO Tables 2023-24 and Census 2021 employment data using FLQ regionalisation (delta=0.3, Lenzen et al. 2017 calibration).

| File | Contents |
|---|---|
| `national-io.json` | National 19x19 Leontief inverse, Type I multipliers, employment/output by ANZSIC division |
| `sa4/*.json` (88 files) | Per-SA4 Type I and Type II multipliers, regional employment, lambda values |

### Parameter Database (`parameters/`)

57 JSON files covering appraisal parameters, unit costs, and construction benchmarks across 8 jurisdictions. Every value is sourced, cited, and version-tracked with staleness detection.

| Directory | Files | Contents |
|---|---|---|
| `uk/` | 19 | Discount rates, carbon values, VSL, QALY, optimism bias, additionality, tax parameters, construction benchmarks, unit costs (GMCA 40+ entries), full GMCA database (674 entries) |
| `au/` | 11 | Discount rates, carbon values, VSL, additionality, tax parameters, construction benchmarks (Rawlinsons), IO metadata, unit costs (RoGS 2026, 54 entries) |
| `us/` | 6 | OMB discount rates, EPA carbon values, VSL, health values |
| `eu/` | 6 | EC discount rates, carbon values, VSL, health values |
| `wb/` | 2 | World Bank ERR parameters |
| `adb/` | 2 | ADB parameters |
| `oecd/` | 2 | OECD benchmark parameters |
| `common/` | 1 | Shared parameters (benefit categories, risk scales) |
| `reference-cases/` | 8 | Asset-type templates with cost benchmarks, benefit categories, published BCR ranges, and typical risks |

### Reference Cases (`parameters/reference-cases/`)

Pre-built templates for common project types, each with cost benchmarks, default parameters, and published BCR ranges from real business cases:

| Template | BCR range | Key references |
|---|---|---|
| UK school (new build) | 1.2-5.0 | DfE, BCIS |
| UK hospital ward | 0.8-8.0 | Midland Met, Royal Liverpool, Papworth |
| UK road scheme | 0.5-6.0 | A14, A303 Stonehenge, Lower Thames Crossing |
| UK rail scheme | 0.3-4.0 | HS2, Crossrail, Beeching reopenings |
| UK housing development | 0.8-3.0 | Homes England, DLUHC |
| UK employment programme | 0.5-4.0 | Work Programme, Future Jobs Fund, Troubled Families |
| UK digital transformation | 0.3-5.0 | Universal Credit, MTD, GOV.UK |
| AU transport infrastructure | 0.5-4.0 | Metro Tunnel, WestConnex, Inland Rail |

## Data Sources

| Source | Coverage | Updated |
|---|---|---|
| ONS (Blue Book, BRES, ASHE, IOAT) | UK macro and LA data | Annual |
| ABS (IO Tables, Census) | Australian IO and regional employment | Annual (IO), 5-yearly (Census) |
| BCIS / Rawlinsons | UK/AU construction cost benchmarks | Quarterly / Annual |
| GMCA Unit Cost Database | 674 UK outcome unit costs | Periodic (latest: Nov 2025) |
| RoGS (Productivity Commission) | 54 Australian service delivery unit costs | Annual (latest: Jan 2026) |
| PSSRU / NHS Reference Costs | UK health unit costs | Annual |
| Home Office HORR99 | UK crime costs | Periodic (latest: 2018) |
| DfT TAG Databook | UK transport values | Annual |
| IHACPA | Australian hospital pricing (NEP) | Annual |

## License

MIT
