"""
Script to capture high-definition live screenshots of MEDNOVA AI screens.
"""

import sys
import os
import time
from pathlib import Path
from PIL import ImageGrab
import tkinter as tk

# Ensure MEDNOVA_AI is in sys.path
sys.path.insert(0, r"C:\Users\ASHISH SHARMA\.gemini\antigravity\scratch\MEDNOVA_AI")

import config
import security
import database
from database import db
from login import LoginWindow
from gui import MainWindow
from billing import ViewInvoiceModal

OUTPUT_DIRS = [
    Path(r"C:\Users\ASHISH SHARMA\.gemini\antigravity\scratch\MEDNOVA_AI\assets\screenshots"),
    Path(r"C:\Users\ASHISH SHARMA\.gemini\antigravity\brain\92c7b1b8-be85-4bd2-a480-3de11df2fe0e")
]

def save_window_capture(win, name):
    win.update_idletasks()
    win.update()
    time.sleep(0.3)
    
    x = win.winfo_rootx()
    y = win.winfo_rooty()
    w = win.winfo_width()
    h = win.winfo_height()
    
    # Grab bbox
    bbox = (max(0, x), max(0, y), x + w, y + h)
    img = ImageGrab.grab(bbox=bbox)
    
    for out_dir in OUTPUT_DIRS:
        out_path = out_dir / f"{name}.png"
        img.save(out_path)
        print(f"Captured: {out_path} ({w}x{h})")

def run_capture():
    db.init_database()
    
    # 1. Capture Login Window
    root = tk.Tk()
    root.withdraw()
    
    login_win = LoginWindow(root, on_success_callback=lambda: None)
    login_win.attributes("-topmost", True)
    login_win.update()
    time.sleep(0.4)
    save_window_capture(login_win, "01_login_screen")
    login_win.destroy()
    root.destroy()
    
    # Authenticate as Admin
    user = db.get_user_by_username("admin")
    security.current_session.set_user(
        user_id=user["id"],
        username=user["username"],
        full_name=user["full_name"],
        role=user["role"],
        email=user["email"]
    )
    
    # 2. Main Window Modules
    app = MainWindow()
    app.attributes("-topmost", True)
    
    # Screen 2: Dashboard
    app.navigate_to("dashboard")
    for _ in range(15):  # Let AI core rotate
        app.update()
        time.sleep(0.04)
    save_window_capture(app, "02_dashboard_screen")
    
    # Screen 3: Patient Registry
    app.navigate_to("patients")
    app.update()
    time.sleep(0.3)
    save_window_capture(app, "03_patients_screen")
    
    # Screen 4: Doctor Roster
    app.navigate_to("doctors")
    app.update()
    time.sleep(0.3)
    save_window_capture(app, "04_doctors_screen")
    
    # Screen 5: Appointments
    app.navigate_to("appointments")
    app.update()
    time.sleep(0.3)
    save_window_capture(app, "05_appointments_screen")
    
    # Screen 6: Medical History
    app.navigate_to("medical_history")
    app.update()
    time.sleep(0.3)
    save_window_capture(app, "06_medical_history_screen")
    
    # Screen 7: Billing
    app.navigate_to("billing")
    app.update()
    time.sleep(0.3)
    save_window_capture(app, "07_billing_screen")
    
    # Screen 8: View Holographic Invoice Modal
    bill = db.get_all_bills()[0]
    patient = db.get_patient_by_id(bill["patient_id"])
    modal = ViewInvoiceModal(app, bill, patient)
    modal.attributes("-topmost", True)
    modal.update()
    time.sleep(0.4)
    save_window_capture(modal, "08_invoice_receipt_modal")
    modal.destroy()
    
    # Screen 9: Canvas Visual Analytics
    app.navigate_to("analytics")
    app.update()
    time.sleep(0.4)
    save_window_capture(app, "09_analytics_screen")
    
    app.destroy()
    print("ALL SCREENSHOTS CAPTURED SUCCESSFULLY!")

if __name__ == "__main__":
    run_capture()
