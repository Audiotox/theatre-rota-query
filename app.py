#!/usr/bin/env python3
"""Flask web app for NHS Theatre Rota Query."""

import os
from flask import Flask, render_template, request
from rota_query import (
    load_file, find_scheduled,
    DAYS, WEEKS, SHIFT_OPTIONS, ALL_BANDS, BAND_COLOURS,
    PINK, PINK_DARK, PINK_LIGHT, PINK_SOFT, HOT_PINK, ROSE,
    MAUVE, PLUM, CORAL, BLUSH, GREY,
)

app = Flask(__name__)

# Load rota data once at startup
ROTA_FILE = os.path.join(os.path.dirname(__file__), 'TWH Flexi working.xlsx')
staff = []
if os.path.exists(ROTA_FILE):
    staff = load_file(ROTA_FILE)

SHIFT_COLOURS = {
    'DAY': PINK,
    'LONG_DAY': CORAL,
    'NIGHT': PLUM,
    'EARLY': '#EC407A',
    'DAY_OFF': GREY,
    'EMPTY': '#CCC',
    'OTHER': '#333',
}


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query_title = ''

    # Defaults
    week = request.form.get('week', 'Week 1')
    day = request.form.get('day', 'Monday')
    shift = request.form.get('shift', 'All Shifts')
    selected_bands = request.form.getlist('bands')

    if not selected_bands:
        selected_bands = ALL_BANDS[:]

    week_num = int(week.split()[-1])
    bands_set = set(selected_bands)
    if staff:
        results = find_scheduled(staff, week_num, day, shift, bands_set)
    query_title = f'Scheduled for {shift} on {day} ({week})'

    # Build results with display info
    display_results = []
    for member, raw, classified in results:
        display_results.append({
            'band': member.band,
            'name': member.name,
            'shift': raw if raw else '-',
            'shift_class': classified,
            'shift_colour': SHIFT_COLOURS.get(classified, '#333'),
            'band_colour': BAND_COLOURS.get(member.band, GREY),
            'hours': member.hours if member.hours else '-',
            'notes': member.comments[:80] + '...' if len(member.comments) > 80 else member.comments,
        })

    return render_template(
        'index.html',
        staff_count=len(staff),
        results=display_results,
        query_title=query_title,
        weeks=WEEKS,
        days=DAYS,
        shift_options=SHIFT_OPTIONS,
        all_bands=ALL_BANDS,
        selected_week=week,
        selected_day=day,
        selected_shift=shift,
        selected_bands=selected_bands,
        band_colours=BAND_COLOURS,
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)
