"""
=============================================================================
MEDNOVA AI — ADVANCED HOSPITAL MANAGEMENT SYSTEM
Module: main.py
Description: Master bootstrapping script. Initializes SQLite database, launches
             the futuristic login gateway, verifies credentials, and instantiates
             the Stark-inspired hospital control center interface.
=============================================================================
"""

import sys
import tkinter as tk
from database import db
from login import LoginWindow
from gui import MainWindow
from security import current_session


def launch_main_application(root_context):
    """Callback triggered after successful operator clearance in LoginWindow."""
    root_context.destroy()
    app = MainWindow()
    # Default to central dashboard on launch
    app.navigate_to("dashboard")
    app.mainloop()


def main():
    """Application entry point."""
    # Ensure database schema and demo records are verified
    db.init_database()

    # Hidden bootstrap root for modal dialog handling
    root = tk.Tk()
    root.withdraw()

    # Launch Stark-inspired Login Gateway
    login_dialog = LoginWindow(
        parent=root,
        on_success_callback=lambda: launch_main_application(root)
    )

    root.mainloop()


if __name__ == "__main__":
    main()
