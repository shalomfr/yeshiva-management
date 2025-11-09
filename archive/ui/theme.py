# -*- coding: utf-8 -*-
"""
מערכת Themes - Theme Management System
"""


class Theme:
    """מחלקה בסיסית לניהול צבעים"""

    def __init__(self):
        self.colors = {}
        self.fonts = {}

    def get_color(self, key):
        """קבלת צבע לפי מפתח"""
        return self.colors.get(key, '#000000')

    def get_font(self, key):
        """קבלת פונט לפי מפתח"""
        return self.fonts.get(key, ('Segoe UI', 12))


class LightTheme(Theme):
    """עיצוב בהיר - Light Modern Theme"""

    def __init__(self):
        super().__init__()

        # צבעים עיקריים
        self.colors = {
            # צבעי גרדיאנט ראשיים - כחול בהיר מודרני
            'gradient_start': '#4A90E2',   # כחול בהיר
            'gradient_mid': '#3E7AD9',     # כחול בינוני
            'gradient_end': '#5BA3FF',     # כחול בהיר ביותר

            # צבעים עיקריים - Light Theme
            'primary': '#4A90E2',           # כחול בהיר ראשי
            'secondary': '#5BA3FF',         # כחול בהיר משני
            'accent': '#FFA726',            # כתום מודרני להדגשות

            # צבעי פעולה
            'success': '#66BB6A',           # ירוק בהיר
            'danger': '#EF5350',            # אדום בהיר
            'warning': '#FFA726',           # כתום בהיר
            'info': '#29B6F6',              # כחול בהיר ביותר

            # רקעים - Light Theme
            'white': '#FFFFFF',
            'bg': '#E8F4F8',                # רקע כחול בהיר ביותר
            'bg_dark': '#D4E8F0',           # רקע כחול בהיר
            'card': '#FFFFFF',              # רקע כרטיסים לבן
            'light': '#F5F9FB',             # רקע בהיר מאוד
            'dark': '#2C3E50',              # טקסט כהה
            'transparent': '#F0F4F7',       # רקע שקוף למחצה בהיר

            # גבולות וצללים - עדינים
            'border': '#D4E8F0',
            'border_light': '#E8F4F8',
            'border_dark': '#C0D9E8',       # גבול בהיר
            'shadow': '#D4E8F0',            # צל עדין
            'shadow_dark': '#C0D9E8',       # צל בהיר

            # טקסט - עיצוב בהיר
            'text': '#2C3E50',              # טקסט כהה
            'text_light': '#7F8C8D',        # טקסט בינוני
            'text_white': '#FFFFFF',        # טקסט לבן
            'inactive': '#B0BEC5',          # טקסט לא פעיל

            # Hover states - Light Theme
            'hover': '#F0F4F7',              # רקע hover בהיר
            'hover_primary': '#3E7AD9',     # hover על primary
            'hover_success': '#5CA965',     # hover על success
            'hover_danger': '#E94B3C'       # hover על danger
        }

        # פונטים
        self.fonts = {
            'title': ('Segoe UI', 32, 'bold'),
            'heading': ('Segoe UI', 20, 'bold'),
            'subheading': ('Segoe UI', 16, 'bold'),
            'normal': ('Segoe UI', 12),
            'bold': ('Segoe UI', 12, 'bold'),
            'small': ('Segoe UI', 10),
            'large': ('Segoe UI', 14),
            'button': ('Segoe UI', 11, 'bold'),
            'header': ('Segoe UI', 28, 'bold'),
            'body': ('Segoe UI', 11)
        }


class DarkTheme(Theme):
    """עיצוב כהה - Dark Theme (עתידי)"""

    def __init__(self):
        super().__init__()

        self.colors = {
            'gradient_start': '#667eea',
            'gradient_mid': '#764ba2',
            'gradient_end': '#f093fb',

            'primary': '#667eea',
            'secondary': '#764ba2',
            'accent': '#f093fb',

            'success': '#4caf50',
            'danger': '#f44336',
            'warning': '#ff9800',
            'info': '#2196f3',

            'white': '#ffffff',
            'bg': '#1e1e1e',
            'bg_dark': '#2d2d2d',
            'card': '#2d2d2d',
            'light': '#3d3d3d',
            'dark': '#ffffff',
            'transparent': '#404040',

            'border': '#404040',
            'border_light': '#505050',
            'border_dark': '#303030',
            'shadow': '#000000',
            'shadow_dark': '#000000',

            'text': '#ffffff',
            'text_light': '#b0b0b0',
            'text_white': '#ffffff',
            'inactive': '#808080',

            'hover': '#3d3d3d',
            'hover_primary': '#5a67d8',
            'hover_success': '#66bb6a',
            'hover_danger': '#ef5350'
        }

        self.fonts = {
            'title': ('Segoe UI', 32, 'bold'),
            'heading': ('Segoe UI', 20, 'bold'),
            'subheading': ('Segoe UI', 16, 'bold'),
            'normal': ('Segoe UI', 12),
            'bold': ('Segoe UI', 12, 'bold'),
            'small': ('Segoe UI', 10),
            'large': ('Segoe UI', 14),
            'button': ('Segoe UI', 11, 'bold'),
            'header': ('Segoe UI', 28, 'bold'),
            'body': ('Segoe UI', 11)
        }
