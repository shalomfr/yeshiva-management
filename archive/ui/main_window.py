# -*- coding: utf-8 -*-
"""
חלון ראשי וניהול עמודים - Main Window & Page Manager
"""

import tkinter as tk
from ui.theme import LightTheme
from ui.components import ModernFrame, ModernButton, ModernLabel


class PageManager:
    """מנהל עמודים דינמי"""

    def __init__(self, root):
        self.root = root
        self.pages = {}
        self.current_page = None
        self.page_frame = None

    def register_page(self, name, page_class):
        """רישום עמוד"""
        self.pages[name] = page_class

    def show_page(self, page_name):
        """הצגת עמוד"""
        if self.current_page:
            if hasattr(self.pages[self.current_page], 'hide'):
                self.pages[self.current_page].hide()

        self.current_page = page_name
        page = self.pages[page_name]

        if hasattr(page, 'show'):
            page.show()
        if hasattr(page, 'refresh'):
            page.refresh()


class MainWindow:
    """חלון ראשי של התוכנה"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🕍 מערכת ניהול ישיבה - עיצוב מודרני")
        self.root.geometry("1400x850")

        # טיפוסגוגוגיה וצבעים
        self.theme = LightTheme()

        # Bind closing with backup
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Page manager
        self.page_manager = PageManager(self.root)

        # Navigation callbacks
        self.nav_callbacks = {}

        # Create main layout
        self.setup_ui()

    def setup_ui(self):
        """הגדרת ממשק"""
        # Main container with sidebar
        main_container = ModernFrame(self.root, theme=self.theme)
        main_container.pack(fill=tk.BOTH, expand=True)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.create_sidebar(main_container)

        # Content area
        content_container = ModernFrame(main_container, theme=self.theme)
        content_container.grid(row=0, column=1, sticky='nsew', padx=0, pady=0)
        content_container.grid_columnconfigure(0, weight=1)
        content_container.grid_rowconfigure(1, weight=1)

        # Header
        self.create_header(content_container)

        # Content area for pages
        self.content_area = ModernFrame(content_container, theme=self.theme)
        self.content_area.grid(row=1, column=0, sticky='nsew')

    def create_sidebar(self, parent):
        """יצירת סרגל צד"""
        sidebar = ModernFrame(parent, theme=self.theme)
        sidebar.config(bg=self.theme.get_color('card'), width=200)
        sidebar.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        sidebar.grid_propagate(False)

        # Logo
        logo_frame = ModernFrame(sidebar, theme=self.theme, use_card_bg=True)
        logo_frame.pack(fill=tk.X, padx=10, pady=10)

        ModernLabel(
            logo_frame,
            text="🕍 מערכת ישיבה",
            theme=self.theme,
            text_type='bold',
            bg=self.theme.get_color('card')
        ).pack(anchor='e', padx=10, pady=10)

        # Navigation items
        nav_items = [
            ("📊", "לוח בקרה", "dashboard"),
            ("👥", "תלמידים", "students"),
            ("📝", "נוכחות", "attendance"),
            ("📊", "דוחות", "reports"),
            ("⚙️", "הגדרות", "settings")
        ]

        for icon, label, page_id in nav_items:
            self.create_nav_button(sidebar, f"{icon} {label}", page_id)

    def create_nav_button(self, parent, text, page_id):
        """יצירת כפתור ניווט"""
        btn = ModernButton(
            parent,
            text=text,
            theme=self.theme,
            on_click=lambda: self.navigate_to(page_id)
        )
        btn.pack(fill=tk.X, padx=10, pady=5)

    def navigate_to(self, page_id):
        """ניווט לעמוד"""
        if page_id in self.nav_callbacks:
            self.nav_callbacks[page_id]()

    def create_header(self, parent):
        """יצירת Header"""
        header = ModernFrame(parent, theme=self.theme)
        header.config(bg=self.theme.get_color('primary'), height=80)
        header.grid(row=0, column=0, sticky='ew')
        header.grid_propagate(False)

        # Title
        title_label = ModernLabel(
            header,
            text="🕍 מערכת ניהול ישיבה",
            theme=self.theme,
            text_type='header',
            bg=self.theme.get_color('primary'),
            fg='white'
        )
        title_label.pack(side=tk.RIGHT, padx=20, pady=10)

    def on_closing(self):
        """סגירה עם גיבוי אוטומטי"""
        from services.database import create_backup, get_data_path
        try:
            db_path = get_data_path("yeshiva_new.db")
            if create_backup(db_path):
                print("✓ גיבוי אוטומטי נוצר בהצלחה")
        except Exception as e:
            print(f"שגיאה ביצירת גיבוי: {e}")
        finally:
            self.root.destroy()

    def run(self):
        """הפעלת התוכנה"""
        self.root.mainloop()

    def get_theme(self):
        """קבלת theme"""
        return self.theme

    def get_content_area(self):
        """קבלת אזור התוכן"""
        return self.content_area
