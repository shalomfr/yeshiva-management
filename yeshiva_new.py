# -*- coding: utf-8 -*-
"""
מערכת ניהול ישיבה - נוסخה מעודכנת
Yeshiva Management System - Updated Version
"""

import tkinter as tk
from ui.main_window import MainWindow
from ui.pages.dashboard import DashboardPage
from ui.pages.students import StudentsPage
from ui.pages.attendance import AttendancePage
from ui.pages.reports import ReportsPage
from ui.pages.settings import SettingsPage


class YeshivaApp:
    """אפליקציית ניהול ישיבה"""

    def __init__(self):
        self.window = MainWindow()
        self.setup_pages()
        self.setup_navigation()
        self.show_dashboard()

    def setup_pages(self):
        """הגדרת עמודים"""
        theme = self.window.get_theme()
        content_area = self.window.get_content_area()

        # Dashboard
        self.dashboard = DashboardPage(content_area, theme)

        # Students
        self.students = StudentsPage(content_area, theme)

        # Attendance
        self.attendance = AttendancePage(content_area, theme)

        # Reports
        self.reports = ReportsPage(content_area, theme)

        # Settings
        self.settings = SettingsPage(content_area, theme)

    def setup_navigation(self):
        """הגדרת צלמי ניווט"""
        self.window.nav_callbacks['dashboard'] = self.show_dashboard
        self.window.nav_callbacks['students'] = self.show_students
        self.window.nav_callbacks['attendance'] = self.show_attendance
        self.window.nav_callbacks['reports'] = self.show_reports
        self.window.nav_callbacks['settings'] = self.show_settings

    def show_dashboard(self):
        """הצגת לוח בקרה"""
        self.dashboard.show()
        self.students.hide()
        self.attendance.hide()
        self.reports.hide()
        self.settings.hide()

    def show_students(self):
        """הצגת ניהול תלמידים"""
        self.dashboard.hide()
        self.students.show()
        self.attendance.hide()
        self.reports.hide()
        self.settings.hide()

    def show_attendance(self):
        """הצגת סימון נוכחות"""
        self.dashboard.hide()
        self.students.hide()
        self.attendance.show()
        self.reports.hide()
        self.settings.hide()

    def show_reports(self):
        """הצגת דוחות"""
        self.dashboard.hide()
        self.students.hide()
        self.attendance.hide()
        self.reports.show()
        self.settings.hide()

    def show_settings(self):
        """הצגת הגדרות"""
        self.dashboard.hide()
        self.students.hide()
        self.attendance.hide()
        self.reports.hide()
        self.settings.show()

    def run(self):
        """הפעלת התוכנה"""
        self.window.run()


def main():
    """הפעלה ראשית"""
    app = YeshivaApp()
    app.run()


if __name__ == "__main__":
    main()
