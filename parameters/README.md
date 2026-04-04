# econstack parameters

Structured CBA parameter database for the `/cost-benefit`, `/io-report`, and `/econ-audit` skills. One JSON file per parameter per jurisdiction.

## Coverage

| Jurisdiction | Files | Parameters |
|---|---|---|
| UK | 10 | Discount rates, carbon values, VSL, health (QALY), VTTS, optimism bias, additionality, tax, distributional weights, construction benchmarks |
| EU | 2 | Discount rates, carbon values (EIB shadow price) |
| AU | 2 | Discount rates, VSL/VSLY |

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
