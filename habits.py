# -*- coding: utf-8 -*-
"""
Created on Fri May 23 12:55:58 2025

@author: Fiona
"""

# habits.py

from datetime import timedelta

def calculate_streak(dates):
    """
    Given a list of datetime.date objects (unsorted), return the current
    consecutive-day streak up to today.
    """
    if not dates:
        return 0

    dates = sorted(set(dates))
    today = dates[-1]
    streak = 1

    i = len(dates) - 1
    while i > 0:
        if dates[i] - dates[i-1] == timedelta(days=1):
            streak += 1
            i -= 1
        else:
            break

    # If the last completion wasn’t today, streak resets to 0
    from datetime import date
    return streak if today == date.today() else 0
