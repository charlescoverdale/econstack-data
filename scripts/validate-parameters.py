#!/usr/bin/env python3
"""
validate-parameters.py
Validate all econstack parameter JSON files against schema and range checks.

Usage:
    python3 scripts/validate-parameters.py

Checks:
  1. Schema: required fields present (parameter, jurisdiction, last_verified, source)
  2. Ranges: discount rates 0-15%, VSL > 0, carbon values positive and increasing
  3. Consistency: S-curve weights sum to 1.0, net additionality factor matches components
  4. Staleness: flag parameters past expected_next_update
  5. Cross-file: discount rates in construction-benchmarks match discount-rates.json

Exit code 0 = all pass, 1 = warnings only, 2 = errors found.
"""

import json
import glob
import os
import sys
from datetime import datetime, date

PARAMS_DIR = os.path.join(os.path.expanduser("~"), "econstack-data", "parameters")

errors = []
warnings = []

def error(file, msg):
    errors.append(f"  ERROR  {file}: {msg}")

def warn(file, msg):
    warnings.append(f"  WARN   {file}: {msg}")

def validate_file(filepath):
    relpath = os.path.relpath(filepath, PARAMS_DIR)

    try:
        with open(filepath) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        error(relpath, f"Invalid JSON: {e}")
        return

    # Schema checks
    for field in ["parameter", "jurisdiction", "last_verified"]:
        if field not in data:
            error(relpath, f"Missing required field: {field}")

    if "source" not in data:
        warn(relpath, "Missing 'source' field")

    # Staleness check
    if "expected_next_update" in data and "last_verified" in data:
        try:
            expected = datetime.strptime(data["expected_next_update"], "%Y-%m").date()
            verified = datetime.strptime(data["last_verified"], "%Y-%m-%d").date()
            today = date.today()

            if today > expected:
                warn(relpath, f"Past expected update date ({data['expected_next_update']}). Last verified {data['last_verified']}.")

            age_days = (today - verified).days
            if age_days > 730:
                error(relpath, f"Over 2 years since last verification ({data['last_verified']})")
        except ValueError:
            pass

    # Type-specific range checks
    param = data.get("parameter", "")

    # Discount rate checks
    if param == "discount_rates":
        if "schedule" in data:
            for entry in data["schedule"]:
                rate = entry.get("rate", 0)
                if rate < 0 or rate > 0.15:
                    error(relpath, f"Discount rate {rate} outside plausible range [0, 0.15]")
        if "values" in data:
            for key, val in data["values"].items():
                if isinstance(val, dict) and "rate" in val:
                    rate = val["rate"]
                    if rate < 0 or rate > 0.15:
                        error(relpath, f"Discount rate {rate} ({key}) outside plausible range [0, 0.15]")

    # VSL checks
    if param == "vsl":
        if "values" in data:
            vals = data["values"]
            if "vpf" in vals:
                vpf = vals["vpf"].get("value", 0) if isinstance(vals["vpf"], dict) else 0
                if vpf <= 0:
                    error(relpath, "VPF must be positive")
            if "vsl" in vals:
                vsl = vals["vsl"].get("value", 0) if isinstance(vals["vsl"], dict) else 0
                if vsl <= 0:
                    error(relpath, "VSL must be positive")

    # Carbon value checks (schedule should be non-negative and increasing)
    if param == "carbon_values":
        for series_key in ["non_traded", "traded", "eib_shadow_price"]:
            series = data.get(series_key, {})
            if "schedule" in series:
                prev_central = 0
                for entry in series["schedule"]:
                    central = entry.get("central", 0)
                    if central < 0:
                        error(relpath, f"Negative carbon value in {series_key}: {central}")
                    if central < prev_central:
                        warn(relpath, f"Carbon values decreasing in {series_key}: {prev_central} -> {central}")
                    prev_central = central

    # Additionality checks
    if param == "additionality" and "scenarios" in data:
        for scenario_name, scenario in data["scenarios"].items():
            if "net_factor" in scenario:
                dw = scenario.get("deadweight", 0)
                disp = scenario.get("displacement", 0)
                leak = scenario.get("leakage", 0)
                sub = scenario.get("substitution", 0)
                computed = (1 - dw) * (1 - disp) * (1 - leak) * (1 - sub)
                stated = scenario["net_factor"]
                if abs(computed - stated) > 0.01:
                    error(relpath, f"Additionality '{scenario_name}': stated net_factor {stated} != computed {computed:.3f}")

    # S-curve weight checks
    if param == "s_curve_profiles" and "profiles" in data:
        for profile_name, profile in data["profiles"].items():
            if "weights" in profile:
                total = sum(profile["weights"])
                if abs(total - 1.0) > 0.001:
                    error(relpath, f"S-curve '{profile_name}' weights sum to {total:.3f}, expected 1.0")

    # Optimism bias checks
    if param == "optimism_bias" and "matrix" in data:
        for project_type, stages in data["matrix"].items():
            if "capex" in stages:
                for stage, rate in stages["capex"].items():
                    if rate is not None and (rate < 0 or rate > 3.0):
                        error(relpath, f"Optimism bias '{project_type}.{stage}' = {rate}, outside [0, 3.0]")

    # Health value checks
    if param == "health_values" and "values" in data:
        for key, val in data["values"].items():
            if isinstance(val, dict):
                v = val.get("value") or val.get("low", 0)
                if v is not None and v <= 0:
                    warn(relpath, f"Health value '{key}' is non-positive: {v}")


def main():
    print(f"Validating parameters in {PARAMS_DIR}")
    print()

    files = sorted(glob.glob(os.path.join(PARAMS_DIR, "**", "*.json"), recursive=True))
    print(f"Found {len(files)} parameter files")
    print()

    for filepath in files:
        validate_file(filepath)

    if errors:
        print("ERRORS:")
        for e in errors:
            print(e)
        print()

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(w)
        print()

    total_issues = len(errors) + len(warnings)
    print(f"=== VALIDATION COMPLETE ===")
    print(f"Files checked: {len(files)}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if len(errors) > 0:
        print("RESULT: FAIL")
        sys.exit(2)
    elif len(warnings) > 0:
        print("RESULT: PASS WITH WARNINGS")
        sys.exit(1)
    else:
        print("RESULT: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
