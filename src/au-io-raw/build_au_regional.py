#!/usr/bin/env python3
"""
Build Australian regional IO multipliers for SA4 regions using FLQ.

Takes:
- National 19x19 direct requirements matrix (from build_au_io.py output)
- SA4 employment by ANZSIC division (Census 2021)

Produces:
- Per-SA4 JSON files with Type I and Type II multipliers
- Matching the UK econstack multipliers.json format
"""

import csv
import json
import math
import os
import re
import numpy as np


ANZSIC_DIVISIONS = [
    ('A', 'Agriculture, forestry & fishing'),
    ('B', 'Mining'),
    ('C', 'Manufacturing'),
    ('D', 'Electricity, gas, water & waste services'),
    ('E', 'Construction'),
    ('F', 'Wholesale trade'),
    ('G', 'Retail trade'),
    ('H', 'Accommodation & food services'),
    ('I', 'Transport, postal & warehousing'),
    ('J', 'Information media & telecommunications'),
    ('K', 'Financial & insurance services'),
    ('L', 'Rental, hiring & real estate services'),
    ('M', 'Professional, scientific & technical services'),
    ('N', 'Administrative & support services'),
    ('O', 'Public administration & safety'),
    ('P', 'Education & training'),
    ('Q', 'Health care & social assistance'),
    ('R', 'Arts & recreation services'),
    ('S', 'Other services'),
]

DIV_LETTERS = [d[0] for d in ANZSIC_DIVISIONS]
DIV_INDEX = {d: i for i, d in enumerate(DIV_LETTERS)}
N_DIV = len(DIV_LETTERS)

# FLQ parameter (Flegg et al. 1995; Lenzen et al. 2017 calibration for Australia)
DELTA = 0.3


def slugify(name):
    """Convert SA4 name to a URL-friendly slug."""
    s = name.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s-]+', '-', s)
    return s


def load_national_io(filepath):
    """Load the national IO data produced by build_au_io.py."""
    with open(filepath) as f:
        data = json.load(f)

    A = np.array(data['direct_requirements'])
    industries = data['industries']

    # National employment and output by division
    nat_emp = np.zeros(N_DIV)
    nat_out = np.zeros(N_DIV)
    emp_per_aud = np.zeros(N_DIV)

    for i, (letter, _) in enumerate(ANZSIC_DIVISIONS):
        info = industries.get(letter, {})
        nat_emp[i] = info.get('employment', 0)
        nat_out[i] = info.get('output_AUDm', 0)
        emp_per_aud[i] = info.get('employment_per_AUDm', 0)

    return A, nat_emp, nat_out, emp_per_aud


def load_sa4_employment(filepath):
    """Load SA4 employment from Census CSV."""
    sa4s = {}  # {(code, name): {division: employment}}

    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            div = row['anzsic_division']
            if div == '_T':  # skip total row
                continue
            if div not in DIV_INDEX:
                continue

            key = (row['sa4_code'], row['sa4_name'], row.get('state_name', ''))
            if key not in sa4s:
                sa4s[key] = np.zeros(N_DIV)

            emp = float(row['employed_persons'])
            sa4s[key][DIV_INDEX[div]] = emp

    # Filter out "no usual address", "migratory", and "other territories" SA4s
    filtered = {}
    for (code, name, state), emp in sa4s.items():
        total = emp.sum()
        if total < 1000:  # skip very small/invalid regions
            continue
        if 'no usual address' in name.lower():
            continue
        if 'migratory' in name.lower():
            continue
        if 'other territories' in name.lower():
            continue
        filtered[(code, name, state)] = emp

    print(f"Loaded {len(filtered)} SA4 regions (filtered from {len(sa4s)})")
    return filtered


def compute_flq(reg_emp, nat_emp, delta=DELTA):
    """Compute Flegg Location Quotient matrix.

    For each pair (i, j):
        CILQ(i,j) = (reg_emp[i] / reg_emp_total) / (nat_emp[i] / nat_emp_total)
                     / ((reg_emp[j] / reg_emp_total) / (nat_emp[j] / nat_emp_total))
        lambda = [log2(1 + reg_emp_total / nat_emp_total)] ^ delta
        FLQ(i,j) = CILQ(i,j) * lambda      if i != j
        FLQ(i,j) = SLQ(i)                   if i == j

    Returns the FLQ matrix (N_DIV x N_DIV).
    """
    reg_total = reg_emp.sum()
    nat_total = nat_emp.sum()

    if reg_total == 0 or nat_total == 0:
        return np.zeros((N_DIV, N_DIV))

    # Lambda: regional size adjustment
    lam = math.log2(1 + reg_total / nat_total) ** delta

    # SLQ for each industry
    slq = np.zeros(N_DIV)
    for i in range(N_DIV):
        if nat_emp[i] > 0 and reg_total > 0:
            slq[i] = (reg_emp[i] / reg_total) / (nat_emp[i] / nat_total)

    # FLQ matrix
    flq = np.zeros((N_DIV, N_DIV))
    for i in range(N_DIV):
        for j in range(N_DIV):
            if i == j:
                flq[i, j] = slq[i]
            else:
                # CILQ = SLQ(i) / SLQ(j)
                if slq[j] > 0:
                    cilq = slq[i] / slq[j]
                    flq[i, j] = cilq * lam
                else:
                    flq[i, j] = 0

    return flq


def regionalise_matrix(A_nat, flq):
    """Apply FLQ to national direct requirements to get regional matrix.

    A_reg[i,j] = A_nat[i,j] * min(FLQ[i,j], 1)

    If FLQ >= 1, the region is self-sufficient in that input; use national coefficient.
    If FLQ < 1, scale down (region imports some of that input).
    """
    A_reg = np.zeros_like(A_nat)
    for i in range(N_DIV):
        for j in range(N_DIV):
            A_reg[i, j] = A_nat[i, j] * min(flq[i, j], 1.0)
    return A_reg


def compute_multipliers(A_reg, nat_emp_per_aud):
    """Compute Type I and Type II multipliers from regional matrix."""
    n = A_reg.shape[0]
    I = np.eye(n)

    # Type I: L = (I - A)^{-1}
    try:
        L = np.linalg.inv(I - A_reg)
    except np.linalg.LinAlgError:
        return None

    output_mult = L.sum(axis=0)

    # Employment multipliers
    emp_mult = np.zeros(n)
    for j in range(n):
        if nat_emp_per_aud[j] > 0:
            total = sum(L[i, j] * nat_emp_per_aud[i] for i in range(n))
            emp_mult[j] = total / nat_emp_per_aud[j]

    # Type II: augment with household row/column
    # Household consumption coefficients estimated from wages share
    # Simplified: assume household spending = 0.6 * compensation of employees
    # and consumption pattern proportional to national output shares
    nat_out_total = 1.0  # normalised
    hh_income_share = 0.35  # average compensation/output ratio
    hh_consumption_rate = 0.6  # propensity to consume from income

    # Augmented matrix (n+1 x n+1)
    A_aug = np.zeros((n + 1, n + 1))
    A_aug[:n, :n] = A_reg

    # Household row: income from each industry (compensation of employees / output)
    for j in range(n):
        A_aug[n, j] = hh_income_share  # simplified

    # Household column: consumption pattern (proportional to regional coefficients column sum)
    col_sums = A_reg.sum(axis=0)
    total_col = col_sums.sum()
    if total_col > 0:
        for i in range(n):
            A_aug[i, n] = hh_consumption_rate * (col_sums[i] / total_col)

    try:
        L2 = np.linalg.inv(np.eye(n + 1) - A_aug)
    except np.linalg.LinAlgError:
        L2 = None

    output_mult_t2 = np.zeros(n)
    emp_mult_t2 = np.zeros(n)

    if L2 is not None:
        for j in range(n):
            output_mult_t2[j] = L2[:n, j].sum()
            if nat_emp_per_aud[j] > 0:
                total = sum(L2[i, j] * nat_emp_per_aud[i] for i in range(n))
                emp_mult_t2[j] = total / nat_emp_per_aud[j]

    return {
        'leontief': L,
        'output_multiplier_type1': output_mult,
        'employment_multiplier_type1': emp_mult,
        'output_multiplier_type2': output_mult_t2,
        'employment_multiplier_type2': emp_mult_t2,
    }


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, '..', '..', 'src', 'data', 'au')

    print("=" * 70)
    print("Building Australian Regional IO Multipliers (SA4 x 19 ANZSIC divisions)")
    print("=" * 70)

    # Load national IO
    national_path = os.path.join(data_dir, 'national-io.json')
    A_nat, nat_emp, nat_out, emp_per_aud = load_national_io(national_path)
    print(f"National matrix: {A_nat.shape}")
    print(f"National employment: {nat_emp.sum():,.0f}")

    # Load SA4 employment
    sa4_emp = load_sa4_employment(os.path.join(base_dir, 'sa4_employment.csv'))

    # Build multipliers for each SA4
    sa4_dir = os.path.join(data_dir, 'sa4')
    os.makedirs(sa4_dir, exist_ok=True)

    results = []

    for (code, name, state), reg_emp in sorted(sa4_emp.items()):
        slug = slugify(name)

        # Compute FLQ
        flq = compute_flq(reg_emp, nat_emp)

        # Lambda for this region
        lam = math.log2(1 + reg_emp.sum() / nat_emp.sum()) ** DELTA

        # Regionalise
        A_reg = regionalise_matrix(A_nat, flq)

        # Compute multipliers
        mults = compute_multipliers(A_reg, emp_per_aud)
        if mults is None:
            print(f"  SKIP {name}: singular matrix")
            continue

        # Build JSON
        sa4_data = {
            'sa4_code': code,
            'sa4_name': name,
            'state': state,
            'source': 'ABS IO Tables 2023-24 + Census 2021 Place of Work',
            'method': 'FLQ',
            'delta': DELTA,
            'lambda': round(lam, 6),
            'total_employment': round(reg_emp.sum(), 0),
            'sectors': {}
        }

        for i, (letter, div_name) in enumerate(ANZSIC_DIVISIONS):
            if nat_out[i] == 0:
                continue
            sa4_data['sectors'][letter] = {
                'name': div_name,
                'regional_employment': round(reg_emp[i], 0),
                'employment_per_AUDm': round(emp_per_aud[i], 4),
                'output_multiplier_type1': round(float(mults['output_multiplier_type1'][i]), 4),
                'employment_multiplier_type1': round(float(mults['employment_multiplier_type1'][i]), 4),
                'output_multiplier_type2': round(float(mults['output_multiplier_type2'][i]), 4),
                'employment_multiplier_type2': round(float(mults['employment_multiplier_type2'][i]), 4),
            }

        # Save
        out_path = os.path.join(sa4_dir, f'{slug}.json')
        with open(out_path, 'w') as f:
            json.dump(sa4_data, f, indent=2)

        avg_mult = np.mean(mults['output_multiplier_type1'][:18])  # exclude S
        results.append((name, state, reg_emp.sum(), lam, avg_mult))

    # Summary
    print(f"\n{'='*80}")
    print(f"Generated multipliers for {len(results)} SA4 regions")
    print(f"{'='*80}")
    print(f"{'SA4':40s} {'State':20s} {'Employment':>12} {'Lambda':>8} {'Avg Mult':>10}")
    print("-" * 92)
    for name, state, emp, lam, avg in sorted(results, key=lambda x: -x[2])[:20]:
        print(f"{name[:40]:40s} {state[:20]:20s} {emp:12,.0f} {lam:8.4f} {avg:10.4f}")
    print(f"... showing top 20 by employment")
    print(f"\nFiles saved to: {sa4_dir}/")


if __name__ == '__main__':
    main()
