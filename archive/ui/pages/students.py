# -*- coding: utf-8 -*-
"""
עמוד ניהול תלמידים - Students Management Page
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
from ui.components import ModernFrame, ModernCard, ModernLabel, ModernButton, ModernEntry
from services.database import YeshivaDatabase
from models.student import Student


class StudentsPage:
    """עמוד ניהול תלמידים"""

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
            text="ניהול תלמידים",
            theme=self.theme,
            text_type='header',
            bg=self.theme.get_color('bg')
        ).pack(anchor='e')

        # Buttons and search
        button_frame = ModernFrame(self.frame, theme=self.theme)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        ModernButton(
            button_frame,
            text="➕ הוסף תלמיד חדש",
            theme=self.theme,
            color_key='success',
            on_click=self.add_student
        ).pack(side=tk.LEFT, padx=5)

        ModernButton(
            button_frame,
            text="🔄 רענן",
            theme=self.theme,
            on_click=self.refresh
        ).pack(side=tk.LEFT, padx=5)

        # Search frame
        search_frame = ModernFrame(self.frame, theme=self.theme)
        search_frame.pack(fill=tk.X, padx=20, pady=10)

        ModernLabel(
            search_frame,
            text="חיפוש:",
            theme=self.theme,
            text_type='normal',
            bg=self.theme.get_color('bg')
        ).pack(side=tk.RIGHT, padx=5)

        self.search_entry = ModernEntry(search_frame, theme=self.theme)
        self.search_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_students())

        # Filter frame
        filter_frame = ModernFrame(self.frame, theme=self.theme)
        filter_frame.pack(fill=tk.X, padx=20, pady=10)

        ModernLabel(
            filter_frame,
            text="סנן לפי כיתה:",
            theme=self.theme,
            text_type='normal',
            bg=self.theme.get_color('bg')
        ).pack(side=tk.RIGHT, padx=5)

        # Grade filter
        self.grade_var = tk.StringVar(value="הכל")
        self.grade_dropdown = tk.OptionMenu(
            filter_frame,
            self.grade_var,
            "הכל", "א'", "ב'", "ג'", "ד'", "ה'", "ו'", "ז'", "ח'",
            command=lambda x: self.apply_filters()
        )
        self.grade_dropdown.config(
            bg=self.theme.get_color('primary'),
            fg='white',
            relief=tk.FLAT
        )
        self.grade_dropdown.pack(side=tk.RIGHT, padx=5)

        # Students list
        list_frame = ModernCard(self.frame, title="רשימת תלמידים", theme=self.theme)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.list_frame = list_frame.get_content_frame()
        self.all_students = []
        self.refresh_students_list()

    def refresh_students_list(self):
        """רענון רשימת התלמידים"""
        # Clear
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        # Get students
        self.all_students = self.db.get_all_students(include_inactive=False)

        if not self.all_students:
            ModernLabel(
                self.list_frame,
                text="אין תלמידים",
                theme=self.theme,
                bg=self.theme.get_color('card')
            ).pack(pady=20)
            return

        # Apply initial filters
        self.apply_filters()

    def search_students(self):
        """חיפוש תלמידים לפי שם"""
        self.apply_filters()

    def apply_filters(self):
        """יישום סינונים וחיפוש"""
        # Clear
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        search_text = self.search_entry.get().lower()
        grade_filter = self.grade_var.get()

        filtered_students = []
        for student in self.all_students:
            # Extract student data
            student_id, first_name, last_name, id_number, birth_date, address, \
                father_name, mother_name, father_phone, mother_phone, home_phone, \
                entry_date, current_grade, initial_grade, status, framework_type, \
                notes, created_at, last_grade_update = student

            # Apply search filter
            full_name = f"{first_name} {last_name}".lower()
            if search_text and search_text not in full_name and search_text not in id_number:
                continue

            # Apply grade filter
            if grade_filter != "הכל" and current_grade != grade_filter:
                continue

            filtered_students.append(student)

        if not filtered_students:
            ModernLabel(
                self.list_frame,
                text="לא נמצאו תלמידים",
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

        # Add filtered students
        for student in filtered_students:
            self.create_student_item(scrollable_frame, student)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_student_item(self, parent, student):
        """יצירת פריט תלמיד"""
        # Extract student data (19 fields from database)
        student_id, first_name, last_name, id_number, birth_date, address, \
            father_name, mother_name, father_phone, mother_phone, home_phone, \
            entry_date, current_grade, initial_grade, status, framework_type, \
            notes, created_at, last_grade_update = student

        item_frame = tk.Frame(parent, bg=self.theme.get_color('light'), relief=tk.FLAT, bd=0)
        item_frame.pack(fill=tk.X, padx=5, pady=5)

        # Student info
        info_frame = tk.Frame(item_frame, bg=self.theme.get_color('light'))
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        full_name = f"{first_name} {last_name}"
        grade = current_grade if current_grade else "לא ידוע"

        ModernLabel(
            info_frame,
            text=full_name,
            theme=self.theme,
            text_type='normal',
            bg=self.theme.get_color('light')
        ).pack(anchor='e')

        ModernLabel(
            info_frame,
            text=f"כיתה: {grade} | ת.ז: {id_number}",
            theme=self.theme,
            text_type='small',
            bg=self.theme.get_color('light')
        ).pack(anchor='e')

        # Buttons
        btn_frame = tk.Frame(item_frame, bg=self.theme.get_color('light'))
        btn_frame.pack(side=tk.LEFT, padx=10, pady=5)

        ModernButton(
            btn_frame,
            text="עריכה",
            theme=self.theme,
            on_click=lambda: self.edit_student(student[0]),
            color_key='primary'
        ).pack(side=tk.LEFT, padx=2)

        ModernButton(
            btn_frame,
            text="מחיקה",
            theme=self.theme,
            on_click=lambda: self.delete_student(student[0]),
            color_key='danger'
        ).pack(side=tk.LEFT, padx=2)

    def add_student(self):
        """הוספת תלמיד חדש"""
        messagebox.showinfo("בנייה", "פונקציית הוספה בעמדה לעדכון")

    def edit_student(self, student_id):
        """עריכת תלמיד"""
        messagebox.showinfo("בנייה", f"עריכה של תלמיד {student_id}")

    def delete_student(self, student_id):
        """מחיקת תלמיד"""
        if messagebox.askyesno("אישור מחיקה", "האם למחוק את התלמיד?"):
            self.db.delete_student(student_id)
            self.refresh()

    def show(self):
        """הצגת העמוד"""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self):
        """הסתרת העמוד"""
        self.frame.pack_forget()

    def refresh(self):
        """רענון"""
        self.refresh_students_list()
