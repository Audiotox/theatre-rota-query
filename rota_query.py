#!/usr/bin/env python3
"""
NHS Theatre Rota Query Tool
Data model and query logic for the rota system.
"""

import openpyxl
import csv
import os
from dataclasses import dataclass, field

# -- Constants --

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
WEEKS = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
SHIFT_OPTIONS = ['All Shifts', 'Day (D)', 'Long Day (LD)', 'Night (N)', 'Early (E)']
ALL_BANDS = ['2', '3', '4', '5', '6', '7', '8']

WEEK_COL_START = {1: 5, 2: 13, 3: 21, 4: 29}
DAY_INDEX = {d: i for i, d in enumerate(DAYS)}

# Pink palette
PINK = '#E91E8C'
PINK_DARK = '#C2185B'
PINK_LIGHT = '#F8BBD0'
PINK_SOFT = '#FCE4EC'
HOT_PINK = '#FF69B4'
ROSE = '#FF007F'
MAUVE = '#E0B0FF'
PLUM = '#9C27B0'
CORAL = '#FF6F61'
BLUSH = '#FFC1CC'
GREY = '#9E9E9E'

BAND_COLOURS = {
    '8': '#E91E8C',
    '7': CORAL,
    '6': '#AB47BC',
    '5': HOT_PINK,
    '4': '#EC407A',
    '3': PLUM,
    '2': MAUVE,
}


# -- Data Model --

@dataclass
class StaffMember:
    band: str
    name: str
    review_date: str
    comments: str
    hours: str
    schedule: dict = field(default_factory=dict)  # (week_int, day_name) -> raw string


def classify_shift(raw: str) -> str:
    """Return one of: DAY, LONG_DAY, NIGHT, EARLY, DAY_OFF, EMPTY, OTHER."""
    if raw is None:
        return 'EMPTY'
    val = str(raw).strip()
    if val == '' or val.lower() == 'none':
        return 'EMPTY'

    upper = val.upper().strip()

    if upper in ('DO', 'OFF', 'D/O', 'DO '):
        return 'DAY_OFF'
    if upper == 'D':
        return 'DAY'
    if upper == 'LD':
        return 'LONG_DAY'
    if upper == 'N':
        return 'NIGHT'
    if upper.startswith('E') and (len(upper) == 1 or upper[1] in ('(', ' ')):
        return 'EARLY'

    # Custom time patterns
    if any(c.isdigit() for c in val):
        if any(x in val for x in ('1900', '19:00', '19.00')):
            return 'LONG_DAY'
        return 'DAY'

    return 'OTHER'


# -- Data Loading --

def load_csv(path: str) -> list:
    staff = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) < 36:
                row.extend([''] * (37 - len(row)))
            band = (row[0] or '').strip()
            name = (row[1] or '').strip()
            if not name or not band or not band.replace(' ', '').isdigit():
                continue
            band = band.strip()
            schedule = {}
            for wk, col_start in WEEK_COL_START.items():
                for day, di in DAY_INDEX.items():
                    idx = col_start + di
                    schedule[(wk, day)] = row[idx].strip() if idx < len(row) else ''
            staff.append(StaffMember(
                band=band,
                name=name,
                review_date=(row[2] or '').strip(),
                comments=(row[3] or '').strip(),
                hours=(row[36] or '').strip() if len(row) > 36 else '',
                schedule=schedule,
            ))
    return staff


def load_xlsx(path: str) -> list:
    staff = []
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    first = True
    for row in ws.iter_rows(values_only=True):
        if first:
            first = False
            continue
        values = list(row)
        while len(values) < 37:
            values.append(None)
        band = str(values[0] or '').strip()
        name = str(values[1] or '').strip()
        if not name or not band or not band.replace(' ', '').isdigit():
            continue
        schedule = {}
        for wk, col_start in WEEK_COL_START.items():
            for day, di in DAY_INDEX.items():
                idx = col_start + di
                raw = values[idx] if idx < len(values) else None
                schedule[(wk, day)] = str(raw).strip() if raw is not None else ''
        staff.append(StaffMember(
            band=band,
            name=name,
            review_date=str(values[2] or '').strip(),
            comments=str(values[3] or '').strip(),
            hours=str(values[36] or '').strip() if values[36] else '',
            schedule=schedule,
        ))
    wb.close()
    return staff


def load_file(path: str) -> list:
    ext = os.path.splitext(path)[1].lower()
    if ext == '.csv':
        return load_csv(path)
    else:
        return load_xlsx(path)


# -- Query Logic --

def parse_shift_choice(choice: str) -> str:
    mapping = {
        'Day (D)': 'DAY',
        'Long Day (LD)': 'LONG_DAY',
        'Night (N)': 'NIGHT',
        'Early (E)': 'EARLY',
        'All Shifts': 'ALL',
    }
    return mapping.get(choice, 'ALL')


def find_scheduled(staff: list, week: int, day: str, shift_type: str, bands: set) -> list:
    results = []
    target = parse_shift_choice(shift_type)

    for m in staff:
        if m.band not in bands:
            continue

        raw = m.schedule.get((week, day), '')
        classified = classify_shift(raw)

        # Skip empty cells and days off
        if classified in ('EMPTY', 'DAY_OFF'):
            continue

        if target == 'ALL' or classified == target:
            results.append((m, raw, classified))

    return sorted(results, key=lambda x: (x[0].band, x[0].name))
