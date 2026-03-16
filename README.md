# Theatre Rota Query Tool

A desktop app for NHS theatre coordinators to quickly find who's scheduled or available for shifts, without scrolling through the spreadsheet.

## What It Does

- **"Who's Scheduled?"** -- Shows all staff currently assigned to a specific shift type on a given day/week
- **"Who's Available?"** -- Shows all staff who have a day off or are unassigned AND whose constraints allow that shift type

## How To Use

### Mac
1. Double-click `Launch Rota Query.command` to open the app
2. Click **Open File** and select the rota spreadsheet (.xlsx or .csv)
3. Pick a **Week** (1-4), **Day**, and **Shift Type** from the dropdowns
4. Click **Who's Scheduled?** or **Who's Available?**
5. Results show staff with their band, current shift, hours, and notes

The app remembers the last file you opened, so next time it loads automatically. Hit **Reload** to refresh data if the spreadsheet has been updated in Excel.

### Windows (Future)
Will be packaged as a standalone .exe -- no Python needed.

## Shift Types

| Code | Meaning |
|------|---------|
| D | Day shift (~08:00-18:00) |
| LD | Long Day (07:30-19:00) |
| N | Night shift |
| E | Early / short shift |
| DO / OFF | Day off |
| (empty) | Unassigned -- treated as available |

## Availability Logic

When searching for **available** staff, the tool:

1. Finds everyone with a day off (DO/OFF) or unassigned (empty cell) on that day
2. Filters out anyone whose comments indicate they can't do that shift:
   - "NO NIGHTS" / "NO NIGHTS OR WKDS" -- excluded from night shift searches
   - "no wkds" / "NO WEEKEND" / "NO NIGHTS WKDS" -- excluded from Fri/Sat/Sun searches
   - "NO LD" / "8-6 only" -- excluded from long day searches
3. Positive overrides are respected:
   - "CAN DO WKD AND NIGHTS" -- keeps them in weekend and night results
   - "CAN DO WKD" -- keeps them in weekend results

## Spreadsheet Format

The tool expects the standard 4-week rota layout:

| Band | Staff Name | Review Date | Comments | WEEK 1 | Mon | Tue | Wed | Thu | Fri | Sat | Sun | WEEK 2 | Mon | ... | Sun | WEEK 3 | ... | WEEK 4 | ... | HOURS |
|------|-----------|-------------|----------|--------|-----|-----|-----|-----|-----|-----|-----|--------|-----|-----|-----|--------|-----|--------|-----|-------|

## Setup (Mac)

Requires Python 3.11+ (system Python 3.9 has an outdated Tk that won't work):

```
python3.11 -m pip install customtkinter openpyxl
```

## Project Files

| File | Purpose |
|------|---------|
| `rota_query.py` | Main application |
| `Launch Rota Query.command` | Double-click launcher (Mac) |
| `README.md` | This file |

## Future Plans

- Package as standalone .exe for Windows 10 (PyInstaller)
- Export filtered results to clipboard
- Day overview tab showing all staff for a given day at a glance
