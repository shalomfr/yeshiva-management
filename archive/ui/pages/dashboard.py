# -*- coding: utf-8 -*-
"""
עמוד לוח בקרה - Dashboard Page
"""

import tkinter as tk
from datetime import datetime
from pyluach import dates
from ui.components import ModernFrame, ModernCard, ModernLabel, ModernButton
from services.database import YeshivaDatabase


class DashboardPage:
    """עמוד לוח בקרה"""

    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.db = YeshivaDatabase()

        self.frame = ModernFrame(parent, theme=theme)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.create_content()

    def create_content(self):
        """יצירת תוכן העמוד"""
        # Title
        title_frame = ModernFrame(self.frame, theme=self.theme)
        title_frame.pack(fill=tk.X, padx=20, pady=20)

        ModernLabel(
            title_frame,
            text="לוח בקרה ראשי",
            theme=self.theme,
            text_type='header',
            bg=self.theme.get_color('bg')
        ).pack(anchor='e')

        # Date
        today = datetime.now()
        heb_date = dates.HebrewDate.from_pydate(today.date())
        date_text = f"תאריך: {heb_date.hebrew_date_string()} | {today.strftime('%d/%m/%Y')}"
        ModernLabel(
            title_frame,
            text=date_text,
            theme=self.theme,
            text_type='body',
            bg=self.theme.get_color('bg')
        ).pack(anchor='e')

        # Stats row
        self.create_stats_row()

        # Cards row
        self.create_cards_row()

    def create_stats_row(self):
        """יצירת תור סטטיסטיקות"""
        stats_frame = ModernFrame(self.frame, theme=self.theme)
        stats_frame.pack(fill=tk.X, padx=20, pady=20)

        # Get data
        students = self.db.get_all_students(include_inactive=False)
        student_count = len(students)

        # Card 1 - Students
        card1 = ModernCard(stats_frame, title="תלמידים נוכחים", theme=self.theme)
        card1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        content1 = card1.get_content_frame()
        ModernLabel(
            content1,
            text=str(student_count),
            theme=self.theme,
            text_type='header',
            bg=self.theme.get_color('card')
        ).pack(pady=20)

        # Card 2 - Classes
        card2 = ModernCard(stats_frame, title="כיתות", theme=self.theme)
        card2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        content2 = card2.get_content_frame()
        ModernLabel(
            content2,
            text="8",
            theme=self.theme,
            text_type='header',
            bg=self.theme.get_color('card')
        ).pack(pady=20)

        # Card 3 - Teachers
        card3 = ModernCard(stats_frame, title="רבנים", theme=self.theme)
        card3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        content3 = card3.get_content_frame()
        ModernLabel(
            content3,
            text="6",
            theme=self.theme,
            text_type='header',
            bg=self.theme.get_color('card')
        ).pack(pady=20)

    def create_cards_row(self):
        """יצירת תור כרטיסים עם ס טטיסטיקות"""
        # Calculate real attendance data
        today = datetime.now().date()
        students = self.db.get_all_students(include_inactive=False)
        total_students = len(students)

        # Get today's attendance
        attendance_data = self.db.get_attendance_for_date(today)
        present_count = len([a for a in attendance_data if a[2] == 'נוכח'])
        absent_count = len([a for a in attendance_data if a[2] == 'חסר'])

        # Calculate attendance percentage
        if total_students > 0:
            attendance_percent = int((present_count / total_students) * 100)
        else:
            attendance_percent = 0

        cards_frame = ModernFrame(self.frame, theme=self.theme)
        cards_frame.pack(fill=tk.X, padx=20, pady=20)
        cards_frame.config(height=140)

        # Weekly attendance stats with real data
        stats = [
            (str(present_count), "נוכחים היום", self.theme.get_color('success')),
            (str(absent_count), "חסרים היום", self.theme.get_color('danger')),
            (f"{attendance_percent}%", "אחוז נוכחות", self.theme.get_color('info')),
            (str(total_students), "תלמידים פעילים", self.theme.get_color('warning'))
        ]

        for value, label, color in stats:
            stat_card = tk.Frame(cards_frame, bg=self.theme.get_color('card'), relief=tk.FLAT, bd=0)
            stat_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Top colored line (thicker for better visibility)
            line = tk.Frame(stat_card, bg=color, height=5)
            line.pack(fill=tk.X)
            line.pack_propagate(False)

            # Content frame with padding
            content_frame = ModernFrame(stat_card, theme=self.theme, use_card_bg=True)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

            # Big number
            ModernLabel(
                content_frame,
                text=value,
                theme=self.theme,
                text_type='header',
                bg=self.theme.get_color('card'),
                fg=color
            ).pack(pady=5)

            # Label
            ModernLabel(
                content_frame,
                text=label,
                theme=self.theme,
                text_type='small',
                bg=self.theme.get_color('card')
            ).pack()

        # Weekly attendance chart
        self.create_weekly_chart()

        # Recent activities placeholder
        activities_frame = ModernCard(self.frame, title="פעילויות אחרונות", theme=self.theme)
        activities_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        activities_content = activities_frame.get_content_frame()
        ModernLabel(
            activities_content,
            text="אין פעילויות אחרונות",
            theme=self.theme,
            text_type='small',
            bg=self.theme.get_color('card')
        ).pack(pady=20)

    def create_weekly_chart(self):
        """יצירת גרף נוכחות שבועי"""
        chart_frame = ModernCard(self.frame, title="נוכחות שבועית", theme=self.theme)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        chart_content = chart_frame.get_content_frame()

        # Create simple bar chart using tkinter
        days = ["א'", "ב'", "ג'", "ד'", "ה'", "ו'"]
        percentages = [95, 92, 88, 90, 87, 85]  # Sample data

        chart_inner = tk.Frame(chart_content, bg=self.theme.get_color('card'))
        chart_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bar chart
        for i, (day, percent) in enumerate(zip(days, percentages)):
            bar_container = tk.Frame(chart_inner, bg=self.theme.get_color('card'))
            bar_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

            # Percentage label
            ModernLabel(
                bar_container,
                text=f"{percent}%",
                theme=self.theme,
                text_type='small',
                bg=self.theme.get_color('card')
            ).pack(anchor='center', pady=5)

            # Bar
            bar_height = 150
            bar_fill = int(bar_height * (percent / 100))

            bar_bg = tk.Frame(bar_container, bg=self.theme.get_color('border'), height=bar_height, width=30)
            bar_bg.pack(expand=True, pady=5)
            bar_bg.pack_propagate(False)

            bar_fill_frame = tk.Frame(bar_bg, bg=self.theme.get_color('success'), height=bar_fill, width=30)
            bar_fill_frame.pack(side=tk.BOTTOM, fill=tk.X)
            bar_fill_frame.pack_propagate(False)

            # Day label
            ModernLabel(
                bar_container,
                text=day,
                theme=self.theme,
                text_type='small',
                bg=self.theme.get_color('card')
            ).pack(anchor='center', pady=5)

    def show(self):
        """הצגת העמוד"""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self):
        """הסתרת העמוד"""
        self.frame.pack_forget()

    def refresh(self):
        """רענון נתונים"""
        pass
