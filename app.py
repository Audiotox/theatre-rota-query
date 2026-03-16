#!/usr/bin/env python3
"""Flask web app for NHS Theatre Rota Query."""

import os
import tempfile
from flask import Flask, render_template, request, session, redirect, url_for, flash
from rota_query import (
    load_file, find_scheduled, classify_shift,
    DAYS, WEEKS, SHIFT_OPTIONS, ALL_BANDS, BAND_COLOURS,
    PINK, PINK_DARK, PINK_LIGHT, PINK_SOFT, HOT_PINK, ROSE,
    MAUVE, PLUM, CORAL, BLUSH, GREY,
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB upload limit

# In-memory storage keyed by session ID
_staff_store = {}


def _get_staff():
    sid = session.get('sid')
    if sid and sid in _staff_store:
        return _staff_store[sid]
    return []


def _set_staff(staff_list):
    import uuid
    if 'sid' not in session:
        session['sid'] = str(uuid.uuid4())
    _staff_store[session['sid']] = staff_list


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
    staff = _get_staff()
    staff_count = len(staff)
    filename = session.get('filename', '')
    results = []
    query_title = ''

    # Defaults
    week = request.form.get('week', 'Week 1')
    day = request.form.get('day', 'Monday')
    shift = request.form.get('shift', 'All Shifts')
    selected_bands = request.form.getlist('bands')

    # On first load or no bands selected, default to all
    if request.method == 'GET' or not selected_bands:
        selected_bands = ALL_BANDS[:]

    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'upload':
            file = request.files.get('file')
            if file and file.filename:
                ext = os.path.splitext(file.filename)[1].lower()
                if ext not in ('.xlsx', '.csv'):
                    flash('Please upload an .xlsx or .csv file.', 'error')
                else:
                    try:
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                        file.save(tmp.name)
                        tmp.close()
                        loaded = load_file(tmp.name)
                        os.unlink(tmp.name)
                        _set_staff(loaded)
                        session['filename'] = file.filename
                        staff = loaded
                        staff_count = len(staff)
                        filename = file.filename
                        flash(f'Loaded {len(loaded)} staff from {file.filename}', 'success')
                    except Exception as e:
                        flash(f'Error loading file: {e}', 'error')
            else:
                flash('No file selected.', 'error')

        if staff:
            week_num = int(week.split()[-1])
            bands_set = set(selected_bands)
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
        staff_count=staff_count,
        filename=filename,
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
