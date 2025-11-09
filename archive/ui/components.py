# -*- coding: utf-8 -*-
"""
רכיבים חוזרים - Reusable UI Components
"""

import tkinter as tk
from tkinter import ttk


class ModernCard(tk.Frame):
    """כרטיס מודרני"""

    def __init__(self, parent, title="", theme=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.theme = theme
        if theme is None:
            self.config(bg='#ffffff')
        else:
            self.config(bg=theme.get_color('card'))

        # Header
        if title:
            header_frame = tk.Frame(self, bg=theme.get_color('primary') if theme else '#4A90E2', height=50)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)

            title_label = tk.Label(
                header_frame,
                text=title,
                font=theme.get_font('subheading') if theme else ('Segoe UI', 16, 'bold'),
                bg=theme.get_color('primary') if theme else '#4A90E2',
                fg='white'
            )
            title_label.pack(padx=20, pady=10, anchor='w')

        # Content frame
        self.content = tk.Frame(self, bg=theme.get_color('card') if theme else '#ffffff')
        self.content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def get_content_frame(self):
        """קבלת frame לתוכן"""
        return self.content


class ModernButton(tk.Button):
    """כפתור מודרני"""

    def __init__(self, parent, text="", theme=None, on_click=None, color_key='primary', **kwargs):
        self.theme = theme
        self.color_key = color_key

        if theme:
            bg_color = theme.get_color(color_key)
            hover_color = theme.get_color(f'hover_{color_key}')
            font = theme.get_font('button')
        else:
            bg_color = '#4A90E2'
            hover_color = '#3E7AD9'
            font = ('Segoe UI', 11, 'bold')

        super().__init__(
            parent,
            text=text,
            bg=bg_color,
            fg='white',
            activebackground=hover_color,
            activeforeground='white',
            relief=tk.FLAT,
            font=font,
            cursor='hand2',
            padx=15,
            pady=10,
            **kwargs
        )

        if on_click:
            self.config(command=on_click)

        self.default_bg = bg_color
        self.hover_bg = hover_color

        # Bind hover effects
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _on_enter(self, event):
        self.config(bg=self.hover_bg)

    def _on_leave(self, event):
        self.config(bg=self.default_bg)


class ModernLabel(tk.Label):
    """תווית מודרנית"""

    def __init__(self, parent, text="", theme=None, text_type='normal', **kwargs):
        self.theme = theme

        if theme:
            font = theme.get_font(text_type)
            text_color = kwargs.pop('fg', theme.get_color('text'))
            bg_color = kwargs.pop('bg', theme.get_color('card'))
        else:
            font = ('Segoe UI', 12)
            text_color = kwargs.pop('fg', '#2C3E50')
            bg_color = kwargs.pop('bg', '#ffffff')

        super().__init__(
            parent,
            text=text,
            font=font,
            fg=text_color,
            bg=bg_color,
            **kwargs
        )


class ModernEntry(tk.Entry):
    """שדה קלט מודרני"""

    def __init__(self, parent, theme=None, **kwargs):
        self.theme = theme

        if theme:
            bg_color = theme.get_color('light')
            fg_color = theme.get_color('text')
            border_color = theme.get_color('border')
            font = theme.get_font('body')
        else:
            bg_color = '#F5F9FB'
            fg_color = '#2C3E50'
            border_color = '#D4E8F0'
            font = ('Segoe UI', 11)

        super().__init__(
            parent,
            bg=bg_color,
            fg=fg_color,
            font=font,
            relief=tk.SOLID,
            bd=1,
            insertbackground=fg_color,
            **kwargs
        )


class ModernFrame(tk.Frame):
    """פריים מודרני"""

    def __init__(self, parent, theme=None, use_card_bg=False, **kwargs):
        self.theme = theme

        if theme:
            if use_card_bg:
                bg = theme.get_color('card')
            else:
                bg = theme.get_color('bg')
        else:
            bg = '#E8F4F8' if not use_card_bg else '#ffffff'

        super().__init__(parent, bg=bg, **kwargs)
