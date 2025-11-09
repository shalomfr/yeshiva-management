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

    @staticmethod
    def parse_hebrew_date(hebrew_date_str):
        """ניסיון להמיר מחרוזת תאריך עברי לתאריך גרגוריאני
        
        מקבל: "א׳ בשבט תשפ״ה" או פורמטים דומים
        מחזיר: datetime.date object או None
        """
        try:
            # ניקוי המחרוזת
            cleaned = hebrew_date_str.strip()
            
            # ניסיון להשתמש ב-pyluach לפרסור
            # pyluach יכול לעבוד עם מחרוזות תאריך עברי
            
            # אם המחרוזת מכילה את המילה "ב" - מנסים לפרסר
            if 'ב' in cleaned:
                parts = cleaned.split()
                if len(parts) >= 3:
                    # מנסים לחלץ מספרים ושמות חודשים
                    from pyluach import parshios
                    
                    # רשימת חודשים עבריים
                    hebrew_months = {
                        'תשרי': 1, 'חשון': 2, 'חשוון': 2, 'כסלו': 3, 'טבת': 4,
                        'שבט': 5, 'אדר': 6, 'אדר א': 6, 'אדר ב': 7,
                        'ניסן': 8, 'אייר': 9, 'סיון': 10, 'סיוון': 10,
                        'תמוז': 11, 'אב': 12, 'אלול': 13
                    }
                    
                    # חילוץ יום, חודש, שנה
                    day_str = parts[0].replace('׳', '').replace("'", '')
                    month_str = parts[1] if len(parts) > 1 else ''
                    year_str = parts[-1].replace('״', '').replace('"', '')
                    
                    # המרת יום עברי למספר
                    day = hebrew_day_to_number(day_str)
                    
                    # חיפוש חודש
                    month = None
                    for heb_month, num in hebrew_months.items():
                        if heb_month in cleaned:
                            month = num
                            break
                    
                    # המרת שנה עברית למספר
                    year = hebrew_year_to_number(year_str)
                    
                    if day and month and year:
                        heb_date = dates.HebrewDate(year, month, day)
                        return heb_date.to_pydate()
            
            return None
        except Exception as e:
            print(f"Error parsing Hebrew date: {e}")
            return None


def hebrew_day_to_number(day_str):
    """המרת יום עברי למספר"""
    hebrew_nums = {
        'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
        'י': 10, 'יא': 11, 'יב': 12, 'יג': 13, 'יד': 14, 'טו': 15, 'טז': 16,
        'יז': 17, 'יח': 18, 'יט': 19, 'כ': 20, 'כא': 21, 'כב': 22, 'כג': 23,
        'כד': 24, 'כה': 25, 'כו': 26, 'כז': 27, 'כח': 28, 'כט': 29, 'ל': 30
    }
    return hebrew_nums.get(day_str, None)


def hebrew_year_to_number(year_str):
    """המרת שנה עברית למספר"""
    # פשטות - נניח שהשנה היא תש"פ = 5780 וכו'
    hebrew_nums = {
        'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
        'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
        'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400
    }
    
    total = 5000  # אלף ה' - המאה ה-6
    for char in year_str:
        if char in hebrew_nums:
            total += hebrew_nums[char]
    
    return total if total > 5000 else None
