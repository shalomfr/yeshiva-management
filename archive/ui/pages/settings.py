# -*- coding: utf-8 -*-
"""
עמוד הגדרות - Settings Page
"""

import tkinter as tk
from tkinter import messagebox
from ui.components import ModernFrame, ModernCard, ModernLabel, ModernButton, ModernEntry
from services.database import YeshivaDatabase


class SettingsPage:
    """עמוד הגדרות"""

    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.db = YeshivaDatabase()

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
            text="הגדרות",
            theme=self.theme,
            text_type='header',
            bg=self.theme.get_color('bg')
        ).pack(anchor='e')

        ModernLabel(
            header_frame,
            text="ניהול כיתות, הרצות משרתת",
            theme=self.theme,
            text_type='small',
            bg=self.theme.get_color('bg')
        ).pack(anchor='e')

        # Classes management
        self.create_classes_section()

        # About section
        self.create_about_section()

    def create_classes_section(self):
        """יצירת סעיף ניהול כיתות"""
        classes_card = ModernCard(self.frame, title="ניהול כיתות", theme=self.theme)
        classes_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        classes_content = classes_card.get_content_frame()

        # Add class button
        btn_frame = ModernFrame(classes_content, theme=self.theme, use_card_bg=True)
        btn_frame.pack(fill=tk.X, pady=15)

        ModernButton(
            btn_frame,
            text="➕ הוסף כיתה חדשה",
            theme=self.theme,
            color_key='success',
            on_click=self.add_class
        ).pack(side=tk.LEFT)

        # Classes list header
        header_frame = tk.Frame(classes_content, bg=self.theme.get_color('light'))
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        headers = ["שם הכיתה", "מספר תלמידים"]
        for header in headers:
            ModernLabel(
                header_frame,
                text=header,
                theme=self.theme,
                text_type='bold',
                bg=self.theme.get_color('light')
            ).pack(side=tk.RIGHT, expand=True, padx=5)

        # Classes list
        list_frame = tk.Frame(classes_content, bg=self.theme.get_color('card'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Get all students and group by class
        students = self.db.get_all_students(include_inactive=False)
        class_counts = {}

        for student in students:
            # Extract grade from student tuple
            # Format: (id, first_name, last_name, id_number, birth_date, address,
            #          father_name, mother_name, father_phone, mother_phone, home_phone,
            #          entry_date, current_grade, initial_grade, status, framework_type, notes, created_at, last_grade_update)
            current_grade = student[12]  # current_grade is at index 12

            if current_grade not in class_counts:
                class_counts[current_grade] = 0
            class_counts[current_grade] += 1

        if class_counts:
            for grade, count in sorted(class_counts.items()):
                class_item = tk.Frame(list_frame, bg=self.theme.get_color('light'))
                class_item.pack(fill=tk.X, padx=10, pady=5)

                ModernLabel(
                    class_item,
                    text=grade if grade else "לא מוגדר",
                    theme=self.theme,
                    text_type='normal',
                    bg=self.theme.get_color('light')
                ).pack(side=tk.RIGHT, expand=True, padx=5)

                ModernLabel(
                    class_item,
                    text=str(count),
                    theme=self.theme,
                    text_type='normal',
                    bg=self.theme.get_color('light')
                ).pack(side=tk.LEFT, expand=True, padx=5)
        else:
            ModernLabel(
                list_frame,
                text="אין תלמידים להצגה",
                theme=self.theme,
                text_type='body',
                bg=self.theme.get_color('card')
            ).pack(pady=30)

    def create_about_section(self):
        """יצירת סעיף About"""
        about_card = ModernCard(self.frame, title="קידוד משרתת", theme=self.theme)
        about_card.pack(fill=tk.BOTH, padx=20, pady=20)

        about_content = about_card.get_content_frame()

        # Version
        version_frame = tk.Frame(about_content, bg=self.theme.get_color('light'))
        version_frame.pack(fill=tk.X, padx=10, pady=10)

        ModernLabel(
            version_frame,
            text="גרסת משרתת",
            theme=self.theme,
            text_type='normal',
            bg=self.theme.get_color('light')
        ).pack(side=tk.RIGHT, expand=True)

        ModernLabel(
            version_frame,
            text="1.0.0",
            theme=self.theme,
            text_type='normal',
            bg=self.theme.get_color('light')
        ).pack(side=tk.LEFT)

        # Status
        status_frame = tk.Frame(about_content, bg=self.theme.get_color('success_light') if hasattr(self.theme.get_color, '__call__') else '#90EE90')
        status_frame.pack(fill=tk.X, padx=10, pady=10)

        ModernLabel(
            status_frame,
            text="סטטוס",
            theme=self.theme,
            text_type='normal',
            bg=self.theme.get_color('success')
        ).pack(side=tk.RIGHT, expand=True)

        ModernLabel(
            status_frame,
            text="פעיל",
            theme=self.theme,
            text_type='normal',
            bg=self.theme.get_color('success')
        ).pack(side=tk.LEFT)

    def add_class(self):
        """הוספת כיתה חדשה"""
        messagebox.showinfo("בנייה", "פונקציית הוספת כיתה בעמדה לעדכון")

    def show(self):
        """הצגת העמוד"""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self):
        """הסתרת העמוד"""
        self.frame.pack_forget()

    def refresh(self):
        """רענון"""
        pass
