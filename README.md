# econstack-data

Pre-processed economic data for 391 UK local authorities. Used by [econstack](https://github.com/charlescoverdale/econstack) skills.

## Contents

Each local authority has 16 JSON files covering:

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

## Installation

```bash
git clone https://github.com/charlescoverdale/econstack-data.git ~/econstack-data
```

Then install [econstack](https://github.com/charlescoverdale/econstack) to use the data.

## License

MIT
