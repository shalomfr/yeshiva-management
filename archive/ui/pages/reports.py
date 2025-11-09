# -*- coding: utf-8 -*-
"""
עמוד דוחות - Reports Page
"""

import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, filedialog
from ui.components import ModernFrame, ModernCard, ModernLabel, ModernButton, ModernEntry
from services.database import YeshivaDatabase
import csv
import os


class ReportsPage:
    """עמוד דוחות נוכחות"""

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
            text="דוחות נוכחות",
            theme=self.theme,
            text_type='header',
            bg=self.theme.get_color('bg')
        ).pack(anchor='e')

        ModernLabel(
            header_frame,
            text="צפייה ויצוא של דוחות נוכחות ודוחות בעבודה",
            theme=self.theme,
            text_type='small',
            bg=self.theme.get_color('bg')
        ).pack(anchor='e')

        # Filters section
        self.create_filters()

        # Report section
        self.create_report_section()

    def create_filters(self):
        """יצירת סינונים"""
        filter_frame = ModernCard(self.frame, title="סינון דוחות", theme=self.theme)
        filter_frame.pack(fill=tk.X, padx=20, pady=20)

        filter_content = filter_frame.get_content_frame()

        # Date range frame
        date_frame = ModernFrame(filter_content, theme=self.theme, use_card_bg=True)
        date_frame.pack(fill=tk.X, pady=10)

        ModernLabel(
            date_frame,
            text="מתאריך",
            theme=self.theme,
            text_type='small',
            bg=self.theme.get_color('card')
        ).pack(side=tk.RIGHT, padx=10)

        self.start_entry = ModernEntry(date_frame, theme=self.theme, width=15)
        self.start_entry.pack(side=tk.RIGHT, padx=5)
        self.start_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime('%d/%m/%Y'))

        ModernLabel(
            date_frame,
            text="עד תאריך",
            theme=self.theme,
            text_type='small',
            bg=self.theme.get_color('card')
        ).pack(side=tk.LEFT, padx=10)

        self.end_entry = ModernEntry(date_frame, theme=self.theme, width=15)
        self.end_entry.pack(side=tk.LEFT, padx=5)
        self.end_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))

        # Class filter frame
        class_frame = ModernFrame(filter_content, theme=self.theme, use_card_bg=True)
        class_frame.pack(fill=tk.X, pady=10)

        ModernLabel(
            class_frame,
            text="כל הכיתות",
            theme=self.theme,
            text_type='small',
            bg=self.theme.get_color('card')
        ).pack(side=tk.RIGHT, padx=10)

        # Report type buttons
        btn_frame = ModernFrame(filter_content, theme=self.theme, use_card_bg=True)
        btn_frame.pack(fill=tk.X, pady=15)

        ModernButton(
            btn_frame,
            text="שבועי",
            theme=self.theme,
            on_click=lambda: self.generate_report('weekly')
        ).pack(side=tk.LEFT, padx=5)

        ModernButton(
            btn_frame,
            text="חודשי",
            theme=self.theme,
            on_click=lambda: self.generate_report('monthly')
        ).pack(side=tk.LEFT, padx=5)

        ModernButton(
            btn_frame,
            text="רבעון",
            theme=self.theme,
            on_click=lambda: self.generate_report('quarterly')
        ).pack(side=tk.LEFT, padx=5)

        ModernButton(
            btn_frame,
            text="יצא לאקסל",
            theme=self.theme,
            color_key='success',
            on_click=lambda: self.export_to_excel()
        ).pack(side=tk.LEFT, padx=5)

    def create_report_section(self):
        """יצירת סעיף הדוחות"""
        report_card = ModernCard(self.frame, title="תוצאות הדוח", theme=self.theme)
        report_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        report_content = report_card.get_content_frame()

        # Table header
        header_frame = tk.Frame(report_content, bg=self.theme.get_color('light'))
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        headers = ["שם", "כיתה", "נוכחויות", "העדרויות", "אחוז"]
        for header in headers:
            ModernLabel(
                header_frame,
                text=header,
                theme=self.theme,
                text_type='bold',
                bg=self.theme.get_color('light')
            ).pack(side=tk.RIGHT, expand=True, padx=5)

        # Table content - placeholder
        content_frame = tk.Frame(report_content, bg=self.theme.get_color('card'))
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ModernLabel(
            content_frame,
            text="אין נתונים להצגה",
            theme=self.theme,
            text_type='body',
            bg=self.theme.get_color('card')
        ).pack(pady=50)

    def generate_report(self, report_type):
        """יצירת דוח"""
        try:
            # Parse dates
            start_date_str = self.start_entry.get()
            end_date_str = self.end_entry.get()

            start_date = datetime.strptime(start_date_str, '%d/%m/%Y').date()
            end_date = datetime.strptime(end_date_str, '%d/%m/%Y').date()

            # Get all students
            students = self.db.get_all_students(include_inactive=False)

            # Generate report
            messagebox.showinfo("דוח", f"דוח {report_type} נוצר בהצלחה\n"
                                       f"מתלמידים {len(students)}\n"
                                       f"מתקופה: {start_date_str} עד {end_date_str}")

        except ValueError:
            messagebox.showerror("שגיאה", "פורמט תאריך לא תקין. השתמש ב-DD/MM/YYYY")

    def export_to_excel(self):
        """ייצוא לאקסל - export as CSV"""
        try:
            # Parse dates
            start_date_str = self.start_entry.get()
            end_date_str = self.end_entry.get()

            start_date = datetime.strptime(start_date_str, '%d/%m/%Y').date()
            end_date = datetime.strptime(end_date_str, '%d/%m/%Y').date()

            # Get all students
            students = self.db.get_all_students(include_inactive=False)

            if not students:
                messagebox.showwarning("אזהרה", "אין תלמידים לייצוא")
                return

            # Ask where to save
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"דוח_נוכחות_{datetime.now().strftime('%Y%m%d')}.csv"
            )

            if not file_path:
                return

            # Prepare data
            rows = []
            rows.append(["שם מלא", "כיתה", "תעודת זהות", "נוכחויות", "העדרויות", "אחוז"])

            for student in students:
                student_id, first_name, last_name, id_number, birth_date, address, \
                    father_name, mother_name, father_phone, mother_phone, home_phone, \
                    entry_date, current_grade, initial_grade, status, framework_type, \
                    notes, created_at, last_grade_update = student

                full_name = f"{first_name} {last_name}"
                grade = current_grade if current_grade else "-"

                # Count attendance
                present = 0
                absent = 0

                # Iterate through date range
                current = start_date
                while current <= end_date:
                    attendance_data = self.db.get_attendance_for_date(current)
                    attendance_status = None

                    for att in attendance_data:
                        if att[0] == student_id:
                            attendance_status = att[2]
                            break

                    if attendance_status == 'נוכח':
                        present += 1
                    elif attendance_status == 'חסר':
                        absent += 1

                    current += timedelta(days=1)

                total_days = (end_date - start_date).days + 1
                percent = int((present / total_days * 100)) if total_days > 0 else 0

                rows.append([full_name, grade, id_number, present, absent, f"{percent}%"])

            # Write to CSV
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(rows)

            messagebox.showinfo("הצלחה", f"הדוח יוצא בהצלחה ל:\n{file_path}")

        except ValueError:
            messagebox.showerror("שגיאה", "פורמט תאריך לא תקין. השתמש ב-DD/MM/YYYY")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בייצוא: {str(e)}")

    def show(self):
        """הצגת העמוד"""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self):
        """הסתרת העמוד"""
        self.frame.pack_forget()

    def refresh(self):
        """רענון"""
        pass
