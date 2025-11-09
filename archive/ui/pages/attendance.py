# -*- coding: utf-8 -*-
"""
עמוד סימון נוכחות - Attendance Page
"""

import tkinter as tk
from datetime import datetime
from pyluach import dates
from ui.components import ModernFrame, ModernCard, ModernLabel, ModernButton
from services.database import YeshivaDatabase
from services.date_service import HebrewDateConverter


class AttendancePage:
    """עמוד סימון נוכחות"""

    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.db = YeshivaDatabase()
        self.current_date = datetime.now()

        self.frame = ModernFrame(parent, theme=theme)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.create_content()

    def create_content(self):
        """יצירת תוכן העמוד"""
        # Header
        header_frame = ModernFrame(self.frame, theme=self.theme)
        header_frame.pack(fill=tk.X, padx=20, pady=20)

        ModernLabel(
            header_frame,
            text="סימון נוכחות",
            theme=self.theme,
            text_type='header',
            bg=self.theme.get_color('bg')
        ).pack(anchor='e')

        # Date selector with navigation
        date_frame = ModernFrame(self.frame, theme=self.theme)
        date_frame.pack(fill=tk.X, padx=20, pady=10)

        heb_date = dates.HebrewDate.from_pydate(self.current_date.date())
        date_text = f"תאריך: {heb_date.hebrew_date_string()} | {self.current_date.strftime('%d/%m/%Y')}"

        ModernLabel(
            date_frame,
            text=date_text,
            theme=self.theme,
            text_type='body',
            bg=self.theme.get_color('bg')
        ).pack(anchor='e', pady=5)

        # Date navigation buttons
        nav_frame = ModernFrame(self.frame, theme=self.theme)
        nav_frame.pack(fill=tk.X, padx=20, pady=5)

        from ui.components import ModernButton
        ModernButton(
            nav_frame,
            text="← יום הקודם",
            theme=self.theme,
            on_click=self.go_to_previous_day
        ).pack(side=tk.RIGHT, padx=5)

        ModernButton(
            nav_frame,
            text="היום",
            theme=self.theme,
            on_click=self.go_to_today
        ).pack(side=tk.RIGHT, padx=5)

        ModernButton(
            nav_frame,
            text="יום הבא →",
            theme=self.theme,
            on_click=self.go_to_next_day
        ).pack(side=tk.RIGHT, padx=5)

        # Stats row for today
        self.create_stats_row()

        # Attendance list
        att_card = ModernCard(self.frame, title="סימון נוכחות", theme=self.theme)
        att_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Quick actions
        actions_frame = ModernFrame(att_card.get_content_frame(), theme=self.theme)
        actions_frame.pack(fill=tk.X, padx=10, pady=10)

        ModernButton(
            actions_frame,
            text="✓ סמן את כולם נוכחים",
            theme=self.theme,
            color_key='success',
            on_click=self.mark_all_present
        ).pack(side=tk.LEFT, padx=5)

        ModernButton(
            actions_frame,
            text="✗ סמן את כולם חסרים",
            theme=self.theme,
            color_key='danger',
            on_click=self.mark_all_absent
        ).pack(side=tk.LEFT, padx=5)

        self.list_frame = tk.Frame(att_card.get_content_frame(), bg=self.theme.get_color('card'))
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.refresh_attendance_list()

    def create_stats_row(self):
        """יצירת שורת סטטיסטיקות יום"""
        stats_frame = ModernFrame(self.frame, theme=self.theme)
        stats_frame.pack(fill=tk.X, padx=20, pady=20)

        # Get today's attendance stats
        attendance_data = self.db.get_attendance_for_date(self.current_date.date())
        students = self.db.get_all_students(include_inactive=False)
        total_students = len(students)

        present_count = len([a for a in attendance_data if a[2] == 'נוכח'])
        absent_count = len([a for a in attendance_data if a[2] == 'חסר'])
        unmarked = total_students - present_count - absent_count

        if total_students > 0:
            attendance_percent = int((present_count / total_students) * 100)
        else:
            attendance_percent = 0

        # Stats cards
        stats = [
            (str(present_count), "נוכחים", self.theme.get_color('success')),
            (str(absent_count), "חסרים", self.theme.get_color('danger')),
            (str(unmarked), "לא סומנו", self.theme.get_color('warning')),
            (f"{attendance_percent}%", "אחוז נוכחות", self.theme.get_color('info'))
        ]

        for value, label, color in stats:
            stat_card = tk.Frame(stats_frame, bg=self.theme.get_color('card'), relief=tk.FLAT, bd=0)
            stat_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Top line
            line = tk.Frame(stat_card, bg=color, height=5)
            line.pack(fill=tk.X)
            line.pack_propagate(False)

            # Content
            content_frame = ModernFrame(stat_card, theme=self.theme, use_card_bg=True)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            ModernLabel(
                content_frame,
                text=value,
                theme=self.theme,
                text_type='header',
                bg=self.theme.get_color('card'),
                fg=color
            ).pack(pady=5)

            ModernLabel(
                content_frame,
                text=label,
                theme=self.theme,
                text_type='small',
                bg=self.theme.get_color('card')
            ).pack()

    def go_to_previous_day(self):
        """עבור ליום הקודם"""
        from datetime import timedelta
        self.current_date -= timedelta(days=1)
        self.refresh()

    def go_to_next_day(self):
        """עבור ליום הבא"""
        from datetime import timedelta
        self.current_date += timedelta(days=1)
        self.refresh()

    def go_to_today(self):
        """חזור להיום"""
        self.current_date = datetime.now()
        self.refresh()

    def mark_all_present(self):
        """סימון כל התלמידים כנוכחים"""
        students = self.db.get_all_students(include_inactive=False)
        heb_date = HebrewDateConverter.get_hebrew_date(self.current_date.date())
        gregorian_date = self.current_date.strftime('%Y-%m-%d')

        for student in students:
            self.db.save_attendance(student[0], heb_date, gregorian_date, 1)

        self.refresh_attendance_list()

    def mark_all_absent(self):
        """סימון כל התלמידים כחסרים"""
        students = self.db.get_all_students(include_inactive=False)
        heb_date = HebrewDateConverter.get_hebrew_date(self.current_date.date())
        gregorian_date = self.current_date.strftime('%Y-%m-%d')

        for student in students:
            self.db.save_attendance(student[0], heb_date, gregorian_date, 0)

        self.refresh_attendance_list()

    def refresh_attendance_list(self):
        """רענון רשימת הנוכחות"""
        # Clear
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        # Get students
        students = self.db.get_all_students(include_inactive=False)

        if not students:
            ModernLabel(
                self.list_frame,
                text="אין תלמידים",
                theme=self.theme,
                bg=self.theme.get_color('card')
            ).pack(pady=20)
            return

        # Create scrollable frame
        canvas = tk.Canvas(self.list_frame, bg=self.theme.get_color('card'), highlightthickness=0)
        scrollbar = tk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme.get_color('card'))

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add students
        for student in students:
            self.create_attendance_item(scrollable_frame, student)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_attendance_item(self, parent, student):
        """יצירת פריט נוכחות"""
        item_frame = tk.Frame(parent, bg=self.theme.get_color('light'))
        item_frame.pack(fill=tk.X, padx=5, pady=5)

        # Student info
        info_frame = tk.Frame(item_frame, bg=self.theme.get_color('light'))
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        full_name = f"{student[1]} {student[2]}"
        ModernLabel(
            info_frame,
            text=full_name,
            theme=self.theme,
            text_type='normal',
            bg=self.theme.get_color('light')
        ).pack(anchor='e')

        # Checkbox buttons
        btn_frame = tk.Frame(item_frame, bg=self.theme.get_color('light'))
        btn_frame.pack(side=tk.LEFT, padx=10, pady=5)

        ModernButton(
            btn_frame,
            text="✓ נוכח",
            theme=self.theme,
            on_click=lambda: self.mark_present(student[0]),
            color_key='success'
        ).pack(side=tk.LEFT, padx=2)

        ModernButton(
            btn_frame,
            text="✗ חסר",
            theme=self.theme,
            on_click=lambda: self.mark_absent(student[0]),
            color_key='danger'
        ).pack(side=tk.LEFT, padx=2)

    def mark_present(self, student_id):
        """סימון נוכח"""
        heb_date = HebrewDateConverter.get_hebrew_date(self.current_date.date())
        gregorian_date = self.current_date.strftime('%Y-%m-%d')
        self.db.save_attendance(student_id, heb_date, gregorian_date, 1)
        self.refresh()

    def mark_absent(self, student_id):
        """סימון חסר"""
        heb_date = HebrewDateConverter.get_hebrew_date(self.current_date.date())
        gregorian_date = self.current_date.strftime('%Y-%m-%d')
        self.db.save_attendance(student_id, heb_date, gregorian_date, 0)
        self.refresh()

    def show(self):
        """הצגת העמוד"""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self):
        """הסתרת העמוד"""
        self.frame.pack_forget()

    def refresh(self):
        """רענון"""
        self.refresh_attendance_list()
