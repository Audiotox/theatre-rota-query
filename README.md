# Theatre Rota Query Tool

A web app for NHS theatre coordinators to quickly find who's scheduled for shifts, without scrolling through the spreadsheet.

Live at: https://theatre-rota-query.onrender.com

## What It Does

- Shows all staff currently assigned to a specific shift type on a given day/week
- Filter by week (1-4), day, shift type, and band
- Results update automatically when any filter is changed

## How To Use

1. Visit the website
2. Pick a **Week** (1-4), **Day**, and **Shift Type** from the dropdowns
3. Toggle **Band** checkboxes to filter by staff band
4. Results update automatically -- no need to click a button

## Updating the Rota

The rota spreadsheet (`TWH Flexi working.xlsx`) is bundled with the app. To update it:

1. Replace the `.xlsx` file in the project folder
2. Commit and push to GitHub
3. Render auto-deploys the update

## Shift Types

| Code | Meaning |
|------|---------|
| D | Day shift (~08:00-18:00) |
| LD | Long Day (07:30-19:00) |
| N | Night shift |
| E | Early / short shift |
| DO / OFF | Day off |
| (empty) | Unassigned |

## Spreadsheet Format

The tool expects the standard 4-week rota layout:

| Band | Staff Name | Review Date | Comments | WEEK 1 | Mon | Tue | Wed | Thu | Fri | Sat | Sun | WEEK 2 | Mon | ... | Sun | WEEK 3 | ... | WEEK 4 | ... | HOURS |
|------|-----------|-------------|----------|--------|-----|-----|-----|-----|-----|-----|-----|--------|-----|-----|-----|--------|-----|--------|-----|-------|

## Project Files

| File | Purpose |
|------|---------|
| `app.py` | Flask web application |
| `rota_query.py` | Data loading and query logic |
| `templates/index.html` | Web page template |
| `static/style.css` | Pink theme styling |
| `static/logo.png` | Header logo |
| `TWH Flexi working.xlsx` | Current rota spreadsheet |
| `requirements.txt` | Python dependencies |
| `render.yaml` | Render deployment config |

## Hosting

Hosted on Render (free tier). The instance sleeps after 15 minutes of inactivity and takes ~30 seconds to wake up on first visit.
