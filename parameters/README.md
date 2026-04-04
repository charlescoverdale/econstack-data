# econstack parameters

Structured CBA parameter database for the `/cost-benefit`, `/io-report`, and `/econ-audit` skills. One JSON file per parameter per jurisdiction.

## Coverage

| Jurisdiction | Files | Parameters |
|---|---|---|
| UK | 14 | Discount rates, carbon values, VSL, health (QALY), VTTS, optimism bias, additionality, tax, distributional weights, construction benchmarks, accident costs (expanded), marginal external costs, fleet assumptions, S-curve profiles |
| US | 6 | Discount rates (OMB A-4 revised + legacy 3%/7%), carbon values (EPA SC-GHG at 3 discount rates), VSL (DOT/EPA/HHS + MAIS injury fractions), health (QALY, DALY, FDA threshold, HHS standard values), VTTS (DOT wage-% method), distributional weights (A-4 revised e=1.4) |
| EU | 6 | Discount rates, carbon values (EIB shadow price), VSL (with member state transfer method), health (QALY/DALY), conversion factors (SCF, shadow wages), distributional weights |
| AU | 6 | Discount rates, VSL/VSLY, health (QALY/DALY), VTTS (formula-based from AWE), accident costs (national + state), carbon values (ACCU + Safeguard Mechanism) |
| OECD | 1 | Cross-country VSL transfer method (income elasticity, GDP per capita for 25+ countries) |

## Schema

Every parameter file has:

- `parameter`: machine-readable identifier
- `jurisdiction`: `uk`, `eu`, `au`
- `label`: human-readable name
- `category`: grouping (appraisal, environment, health, transport, fiscal, validation)
- `source`: publication, publisher, URL, date, update frequency
- `last_verified`: date these values were checked against the source

Values come in three shapes:

**Point values** (VSL, QALY):
```json
{ "values": { "central": 2350000, "low": null, "high": null } }
```

**Time series** (carbon prices, discount rates):
```json
{ "schedule": [{ "year": 2025, "low": 127, "central": 254, "high": 381 }] }
```

**Matrix** (optimism bias):
```json
{ "matrix": { "standard_buildings": { "soc": 0.24, "obc": 0.04, "fbc": 0.02 } } }
```

## How the skills use these

The `/cost-benefit` skill loads parameters from `~/econstack-data/parameters/{jurisdiction}/` based on the detected framework. If the parameter files are not found, the skill falls back to built-in defaults.

The `/io-report` skill loads `uk/tax-parameters.json` for tax revenue estimates.

The `/econ-audit` skill loads parameters to validate against (checking that CBAs use the correct discount rates, plausible multiplier ranges, etc.).

## Updating values

Most parameters update annually. When a source publishes new values:

1. Download the latest publication (TAG Data Book, DESNZ carbon values, etc.)
2. Update the relevant JSON file with the new values
3. Update `price_base_year` and `last_verified`
4. Commit and push to econstack-data

For UK transport parameters, the TAG Data Book (.xlsm) is the primary source. Download from GOV.UK and cross-check against the JSON files.

### Extraction scripts

Two R scripts in `scripts/` help with updates:

- `scripts/extract-tag-databook.R <file.xlsm>` : Reads a TAG Data Book and previews VTTS and accident cost sheets for manual extraction
- `scripts/extract-desnz-carbon.R [file.xlsx]` : Reads DESNZ carbon values spreadsheet, or shows current values for manual update

## Sources

| Parameter | Source | URL |
|---|---|---|
| UK discount rates | Green Book 2026 | gov.uk/government/publications/the-green-book |
| UK carbon values | DESNZ valuation guidance | gov.uk/government/publications/valuing-greenhouse-gas-emissions-in-policy-appraisal |
| UK VPF / accident costs | TAG Data Book v2.02 | gov.uk/government/publications/tag-data-book |
| UK QALY | Green Book / DHSC | gov.uk/government/publications/the-green-book |
| UK VTTS | TAG Data Book v2.02 | gov.uk/government/publications/tag-data-book |
| UK optimism bias | Green Book supplementary guidance | gov.uk/government/publications/green-book-supplementary-guidance-optimism-bias |
| UK additionality | HM Treasury Additionality Guide 4th ed | gov.uk/government/publications/green-book-supplementary-guidance-additionality |
| UK tax rates | HMRC | gov.uk/government/publications/rates-and-allowances-income-tax |
| EU discount rates | EC DG Regio CBA Guide 2014 | ec.europa.eu/regional_policy |
| EU carbon values | EIB Climate Bank Roadmap | eib.org |
| AU discount rates | ATAP / Infrastructure Australia | atap.gov.au |
| AU VSL | Office of Impact Analysis | oia.pmc.gov.au |
| UK accident costs (expanded) | TAG Data Book A4.1 | gov.uk/government/publications/tag-data-book |
| UK marginal external costs | TAG Data Book A5.4 | gov.uk/government/publications/tag-data-book |
| UK fleet assumptions | TAG Data Book A1.3, A3 | gov.uk/government/publications/tag-data-book |
| UK S-curve profiles | Green Book 2026 | gov.uk/government/publications/the-green-book |
| EU VSL | EC CBA Guide + OECD 2025 | ec.europa.eu/regional_policy |
| EU health values | EC CBA Guide + EUnetHTA | ec.europa.eu/regional_policy |
| EU conversion factors | EC CBA Guide Ch. 2 | ec.europa.eu/regional_policy |
| EU distributional weights | EC CBA Guide S. 2.9 | ec.europa.eu/regional_policy |
| AU health values | PBAC / OIA | oia.pmc.gov.au |
| AU VTTS | ATAP PV2 | atap.gov.au |
| AU accident costs | ATAP PV2 / BITRE | atap.gov.au |
| AU carbon values | Clean Energy Regulator | cleanenergyregulator.gov.au |
