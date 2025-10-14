"""
Theme Manager - Dark/Light/System Default Themes
Provides theme switching capability

SEPARATION OF CONCERNS: Theme management only
"""

import tkinter as tk
from tkinter import ttk


class ThemeManager:
    """Manage application themes"""
    
    THEMES = {
        'system': {
            'name': 'System Default',
            'bg': '#f0f0f0',
            'fg': '#000000',
            'text_bg': '#ffffff',
            'text_fg': '#000000',
            'button_bg': '#e1e1e1',
            'button_fg': '#000000',
            'select_bg': '#0078d7',
            'select_fg': '#ffffff',
            'menu_bg': '#f0f0f0',
            'menu_fg': '#000000'
        },
        'light': {
            'name': 'Light Mode',
            'bg': '#ffffff',
            'fg': '#2d3748',
            'text_bg': '#f7fafc',
            'text_fg': '#1a202c',
            'button_bg': '#667eea',
            'button_fg': '#ffffff',
            'select_bg': '#667eea',
            'select_fg': '#ffffff',
            'menu_bg': '#edf2f7',
            'menu_fg': '#2d3748'
        },
        'dark': {
            'name': 'Dark Mode',
            'bg': '#1a202c',
            'fg': '#e2e8f0',
            'text_bg': '#2d3748',
            'text_fg': '#f7fafc',
            'button_bg': '#4a5568',
            'button_fg': '#e2e8f0',
            'select_bg': '#667eea',
            'select_fg': '#ffffff',
            'menu_bg': '#2d3748',
            'menu_fg': '#e2e8f0'
        }
    }
    
    def __init__(self, root):
        self.root = root
        self.current_theme = 'system'
        self._create_styles()
    
    def _create_styles(self):
        """Create ttk styles for theming"""
        self.style = ttk.Style(self.root)
        
        # Available TTK themes
        available_themes = self.style.theme_names()
        
        # Try to use a modern theme if available
        if 'clam' in available_themes:
            self.style.theme_use('clam')
        elif 'alt' in available_themes:
            self.style.theme_use('alt')
    
    def apply_theme(self, theme_name='system'):
        """Apply a theme to the application"""
        if theme_name not in self.THEMES:
            theme_name = 'system'
        
        theme = self.THEMES[theme_name]
        self.current_theme = theme_name
        
        # Configure root window
        self.root.configure(bg=theme['bg'])
        
        # Configure ttk styles
        self.style.configure('TFrame', background=theme['bg'])
        self.style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
        self.style.configure('TButton', 
                           background=theme['button_bg'], 
                           foreground=theme['button_fg'],
                           borderwidth=1,
                           relief='raised')
        self.style.map('TButton',
                      background=[('active', theme['select_bg']),
                                ('pressed', theme['select_bg'])],
                      foreground=[('active', theme['select_fg']),
                                ('pressed', theme['select_fg'])])
        
        # Configure Text widget styles
        self.style.configure('TNotebook', background=theme['bg'])
        self.style.configure('TNotebook.Tab', 
                           background=theme['menu_bg'], 
                           foreground=theme['menu_fg'])
        self.style.map('TNotebook.Tab',
                      background=[('selected', theme['select_bg'])],
                      foreground=[('selected', theme['select_fg'])])
        
        # Title label style
        self.style.configure('Title.TLabel',
                           font=('Arial', 16, 'bold'),
                           background=theme['bg'],
                           foreground=theme['fg'])
        
        # Update all existing widgets
        self._update_widgets(self.root, theme)
        
        return theme_name
    
    def _update_widgets(self, widget, theme):
        """Recursively update all widgets"""
        # Update Text widgets
        if isinstance(widget, tk.Text):
            widget.configure(
                bg=theme['text_bg'],
                fg=theme['text_fg'],
                insertbackground=theme['text_fg'],
                selectbackground=theme['select_bg'],
                selectforeground=theme['select_fg']
            )
        
        # Update Frame widgets
        elif isinstance(widget, tk.Frame):
            widget.configure(bg=theme['bg'])
        
        # Update Label widgets
        elif isinstance(widget, tk.Label):
            widget.configure(bg=theme['bg'], fg=theme['fg'])
        
        # Update Button widgets (tk.Button, not ttk.Button)
        elif isinstance(widget, tk.Button):
            widget.configure(
                bg=theme['button_bg'],
                fg=theme['button_fg'],
                activebackground=theme['select_bg'],
                activeforeground=theme['select_fg']
            )
        
        # Update Menu widgets
        elif isinstance(widget, tk.Menu):
            widget.configure(
                bg=theme['menu_bg'],
                fg=theme['menu_fg'],
                activebackground=theme['select_bg'],
                activeforeground=theme['select_fg']
            )
        
        # Recursively update children
        try:
            for child in widget.winfo_children():
                self._update_widgets(child, theme)
        except:
            pass
    
    def get_current_theme(self):
        """Get current theme name"""
        return self.current_theme
    
    def get_theme_names(self):
        """Get list of available theme names"""
        return list(self.THEMES.keys())
    
    @staticmethod
    def get_theme_display_name(theme_name):
        """Get display name for theme"""
        return ThemeManager.THEMES.get(theme_name, {}).get('name', theme_name.title())
