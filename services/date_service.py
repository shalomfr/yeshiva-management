# -*- coding: utf-8 -*-
"""
שירות המרת תאריכים - Date Service
"""

from datetime import date, timedelta
from pyluach import dates


class HebrewDateConverter:
    """ממיר תאריכים עברי"""

    @staticmethod
    def get_current_hebrew_date():
        """תאריך עברי נוכחי"""
        today = date.today()
        heb_date = dates.HebrewDate.from_pydate(today)
        return heb_date.hebrew_date_string()

    @staticmethod
    def get_hebrew_date(pydate):
        """המרת תאריך פייתון לעברי"""
        heb_date = dates.HebrewDate.from_pydate(pydate)
        return heb_date.hebrew_date_string()

    @staticmethod
    def get_week_dates():
        """קבלת תאריכי השבוע הנוכחי (א-ו)"""
        today = date.today()
        days_since_sunday = (today.weekday() + 1) % 7
        sunday = today - timedelta(days=days_since_sunday)

        week_dates = []
        for i in range(6):
            current_date = sunday + timedelta(days=i)
            week_dates.append(current_date)

        return week_dates
