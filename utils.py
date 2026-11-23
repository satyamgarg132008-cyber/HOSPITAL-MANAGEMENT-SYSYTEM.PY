"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: utils.py
Description: Mathematical financial utilities, input validation, date converters,
             custom GUI widget builders, and printable ASCII invoice generation.
=============================================================================
"""

import re
import datetime
from decimal import Decimal, ROUND_HALF_UP
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from typing import Tuple, Optional
import config


def format_currency(amount: float | Decimal | int) -> str:
    """Format any numeric amount into standard USD currency notation."""
    try:
        dec = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"${dec:,.2f}"
    except Exception:
        return "$0.00"


def calculate_age_from_dob(dob_str: str) -> int:
    """Calculate exact integer age from 'YYYY-MM-DD' date string."""
    try:
        born = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    except Exception:
        return 0


def validate_email(email: str) -> bool:
    """Validate standard RFC email format."""
    if not email:
        return True  # Email is optional in most forms
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email.strip()) is not None


def validate_phone(phone: str) -> bool:
    """Ensure phone number contains at least 7 digits."""
    digits = re.sub(r"\D", "", phone)
    return len(digits) >= 7


def parse_decimal(value_str: str) -> Tuple[bool, Decimal]:
    """Parse string input into a precise Decimal. Returns (is_valid, Decimal)."""
    try:
        val = Decimal(str(value_str).strip())
        if val < 0:
            return False, Decimal("0.00")
        return True, val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        return False, Decimal("0.00")


# =============================================================================
# FUTURISTIC TKINTER WIDGET FACTORIES & DECORATORS
# =============================================================================

def create_holographic_card(parent, title: str = "", subtitle: str = "", border_color=config.ACCENT_BORDER) -> tk.Frame:
    """
    Creates a Tony Stark sci-fi holographic-styled card container
    with a cybernetic header line and dark-glass canvas.
    """
    card = tk.Frame(parent, bg=config.BG_CARD, highlightthickness=1, highlightbackground=border_color)
    
    if title:
        header_frame = tk.Frame(card, bg=config.BG_CARD)
        header_frame.pack(fill=tk.X, padx=12, pady=(10, 4))
        
        lbl_title = tk.Label(
            header_frame,
            text=f"◈ {title.upper()}",
            font=config.FONT_CARD_LABEL,
            fg=config.ACCENT_CYAN,
            bg=config.BG_CARD
        )
        lbl_title.pack(side=tk.LEFT)
        
        if subtitle:
            lbl_sub = tk.Label(
                header_frame,
                text=subtitle,
                font=config.FONT_SMALL,
                fg=config.COLOR_TEXT_SECONDARY,
                bg=config.BG_CARD
            )
            lbl_sub.pack(side=tk.RIGHT)
            
        # Subtle horizontal divider line
        divider = tk.Frame(card, bg=border_color, height=1)
        divider.pack(fill=tk.X, padx=12, pady=(2, 8))
        
    return card


class GlowingButton(tk.Button):
    """
    Custom Tkinter Button with animated sci-fi glowing hover states.
    Supports preset themes: 'cyan', 'blue', 'green', 'danger', and 'ghost'.
    """
    def __init__(self, master=None, theme="cyan", **kwargs):
        self.theme = theme
        
        if theme == "cyan":
            self.normal_bg = "#002B3D"
            self.hover_bg = config.ACCENT_CYAN
            self.normal_fg = config.ACCENT_CYAN
            self.hover_fg = "#050814"
            self.border_col = config.ACCENT_CYAN
        elif theme == "blue":
            self.normal_bg = "#001D4A"
            self.hover_bg = config.ACCENT_BLUE
            self.normal_fg = "#60A5FA"
            self.hover_fg = "#FFFFFF"
            self.border_col = config.ACCENT_BLUE
        elif theme == "green":
            self.normal_bg = "#00331D"
            self.hover_bg = config.ACCENT_GREEN
            self.normal_fg = config.ACCENT_GREEN
            self.hover_fg = "#050814"
            self.border_col = config.ACCENT_GREEN
        elif theme == "danger":
            self.normal_bg = "#3B0814"
            self.hover_bg = config.ACCENT_DANGER
            self.normal_fg = config.ACCENT_DANGER
            self.hover_fg = "#FFFFFF"
            self.border_col = config.ACCENT_DANGER
        else: # ghost / neutral
            self.normal_bg = config.BG_CARD
            self.hover_bg = config.BG_CARD_HOVER
            self.normal_fg = config.COLOR_TEXT_SECONDARY
            self.hover_fg = config.COLOR_TEXT_PRIMARY
            self.border_col = config.ACCENT_BORDER

        kwargs.setdefault("bg", self.normal_bg)
        kwargs.setdefault("fg", self.normal_fg)
        kwargs.setdefault("activebackground", self.hover_bg)
        kwargs.setdefault("activeforeground", self.hover_fg)
        kwargs.setdefault("font", config.FONT_BODY_BOLD)
        kwargs.setdefault("relief", tk.FLAT)
        kwargs.setdefault("cursor", "hand2")
        kwargs.setdefault("bd", 0)
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("highlightbackground", self.border_col)
        kwargs.setdefault("padx", 14)
        kwargs.setdefault("pady", 6)
        
        super().__init__(master, **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        self.configure(bg=self.hover_bg, fg=self.hover_fg)

    def _on_leave(self, event=None):
        self.configure(bg=self.normal_bg, fg=self.normal_fg)


def create_form_entry(parent, label_text: str, default_val: str = "", show: str = None) -> Tuple[tk.Frame, tk.Entry]:
    """Helper to build a futuristic form input with label and neon highlight border."""
    container = tk.Frame(parent, bg=config.BG_CARD)
    container.pack(fill=tk.X, pady=6)
    
    lbl = tk.Label(
        container,
        text=label_text,
        font=config.FONT_BODY_BOLD,
        fg=config.COLOR_TEXT_SECONDARY,
        bg=config.BG_CARD
    )
    lbl.pack(anchor=tk.W, pady=(0, 2))
    
    entry_border = tk.Frame(container, bg=config.ACCENT_BORDER, padx=1, pady=1)
    entry_border.pack(fill=tk.X)
    
    entry = tk.Entry(
        entry_border,
        bg=config.BG_INPUT,
        fg=config.COLOR_TEXT_PRIMARY,
        insertbackground=config.ACCENT_CYAN,
        relief=tk.FLAT,
        font=config.FONT_BODY,
        show=show
    )
    entry.pack(fill=tk.X, ipady=6, padx=4)
    
    if default_val:
        entry.insert(0, default_val)
        
    def on_focus_in(e):
        entry_border.configure(bg=config.ACCENT_CYAN)
    def on_focus_out(e):
        entry_border.configure(bg=config.ACCENT_BORDER)
        
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    
    return container, entry


def export_treeview_to_csv(tree: ttk.Treeview, default_filename: str):
    """Generic exporter to save any Treeview's visible data into a clean CSV file."""
    filepath = filedialog.asksaveasfilename(
        initialdir=str(config.EXPORTS_DIR),
        initialfile=default_filename,
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if not filepath:
        return
        
    try:
        columns = [tree.heading(col)["text"] for col in tree["columns"]]
        rows = []
        for item in tree.get_children():
            rows.append(tree.item(item)["values"])
            
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
            
        messagebox.showinfo("Export Successful", f"Data exported successfully to:\n{filepath}")
    except Exception as e:
        messagebox.showerror("Export Failed", f"Could not export CSV file:\n{str(e)}")


def generate_ascii_invoice_text(invoice_data: dict, patient_data: dict) -> str:
    """Format an itemized, cyber-themed medical billing receipt string."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    subtotal = Decimal(str(invoice_data["consultation_fee"])) + Decimal(str(invoice_data["service_charges"]))
    tax_amt = (subtotal * Decimal(str(invoice_data["tax_percent"]))) / Decimal("100")
    total_amt = Decimal(str(invoice_data["total_amount"]))
    
    lines = [
        "==========================================================================",
        "                     MEDNOVA AI HEALTH SYSTEMS",
        "          QUANTUM MEDICAL CENTER • DIVISION OF CLINICAL EXCELLENCE",
        "                10880 MALIBU POINT, SECTOR 4, CA 90265",
        "                 PHONE: +1-800-555-NOVA • WEB: MEDNOVA.AI",
        "==========================================================================",
        f"  INVOICE NUMBER : {invoice_data.get('invoice_no', 'N/A'):<24} DATE: {invoice_data.get('bill_date', now_str[:10])}",
        f"  PAYMENT STATUS : {invoice_data.get('payment_status', 'Pending'):<24} METHOD: {invoice_data.get('payment_method', 'N/A')}",
        "--------------------------------------------------------------------------",
        "  PATIENT DOSSIER:",
        f"  Name           : {patient_data.get('full_name', 'N/A')}",
        f"  Patient UID    : {patient_data.get('patient_uid', 'N/A')}",
        f"  Age / Gender   : {patient_data.get('age', 'N/A')} yrs / {patient_data.get('gender', 'N/A')}",
        f"  Blood Group    : {patient_data.get('blood_group', 'N/A')}",
        f"  Emergency Cont : {patient_data.get('emergency_contact', 'N/A')}",
        "--------------------------------------------------------------------------",
        "  ITEMIZED CLINICAL CHARGES:",
        f"  1. Specialist Physician Consultation ...................... {format_currency(invoice_data.get('consultation_fee', 0.0)):>12}",
        f"  2. Diagnostic Labs / Clinical Procedures .................. {format_currency(invoice_data.get('service_charges', 0.0)):>12}",
        "--------------------------------------------------------------------------",
        f"  SUBTOTAL ................................................. {format_currency(subtotal):>12}",
        f"  HEALTHCARE SURCHARGE / TAX ({invoice_data.get('tax_percent', 0.0)}%) ................ {format_currency(tax_amt):>12}",
        "==========================================================================",
        f"  TOTAL DUE / SETTLED ...................................... {format_currency(total_amt):>12}",
        "==========================================================================",
        f"  CLINICAL NOTES : {invoice_data.get('notes', 'Routine Consultation & Care Services')}",
        "",
        "  SYSTEM VERIFICATION: J.A.R.V.I.S. SECURE CRYPTO-SIGNATURE CERTIFIED",
        f"  GENERATED ON : {now_str}",
        "==========================================================================",
        "       SMART HEALTHCARE • INTELLIGENT MANAGEMENT • MEDNOVA AI 2026",
        "=========================================================================="
    ]
    return "\n".join(lines)
