"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: config.py
Description: System-wide configuration, futuristic color palette, typography,
             window metrics, and role-based access control constants.
=============================================================================
"""

import os
from pathlib import Path

# --- DIRECTORY PATHS ---
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "mednova.db"
INVOICES_DIR = BASE_DIR / "invoices"
EXPORTS_DIR = BASE_DIR / "exports"

# Auto-create output directories if they do not exist
INVOICES_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# --- APPLICATION METADATA ---
APP_NAME = "MEDNOVA AI"
APP_SUBTITLE = "INTELLIGENT HOSPITAL MANAGEMENT SYSTEM"
APP_TAGLINE = "Smart Healthcare. Intelligent Management."
APP_VERSION = "v3.8.0-QUANTUM"
COPYRIGHT_TEXT = "MEDNOVA AI SYSTEMS © 2026 • UNIVERSITY PROJECT EDITION"

# --- WINDOW SPECIFICATIONS ---
WINDOW_MIN_WIDTH = 1280
WINDOW_MIN_HEIGHT = 800
WINDOW_DEFAULT_WIDTH = 1366
WINDOW_DEFAULT_HEIGHT = 860

# --- TONY STARK J.A.R.V.I.S.-INSPIRED COLOR PALETTE ---
# Deep space & navy backgrounds
BG_DARK = "#050814"        # Primary abyss black/navy
BG_PANEL = "#0A1128"       # Slightly lighter navy for sidebars & containers
BG_CARD = "#0D1B36"        # Holographic card background
BG_CARD_HOVER = "#13254A"  # Interactive card hover
BG_INPUT = "#081326"       # Form input fields
BG_TABLE_ROW_ALT = "#0A152C"# Alternating table row background

# Neon Accents & Holographic Glows
ACCENT_CYAN = "#00F0FF"    # Arc Reactor Neon Cyan (Primary highlight)
ACCENT_BLUE = "#0080FF"    # Electric Cobalt Blue
ACCENT_PURPLE = "#8B5CF6"  # Quantum Violet accent
ACCENT_GREEN = "#00FF88"   # Neon Emerald (Online / Success / Healthy)
ACCENT_AMBER = "#FFB800"   # Cyber Warning Amber
ACCENT_DANGER = "#FF2E63"  # Neon Crimson (Critical / Delete / Emergency)
ACCENT_BORDER = "#1E3A5F"  # Subtle glowing border outline
ACCENT_BORDER_GLOW = "#00D2E6" # Active border highlight

# Typography Colors
COLOR_TEXT_PRIMARY = "#FFFFFF"   # Bright white for titles and primary labels
COLOR_TEXT_SECONDARY = "#94A3B8" # Muted slate for secondary labels
COLOR_TEXT_CYAN = "#00F0FF"      # Neon cyan emphasis text
COLOR_TEXT_MUTED = "#526581"     # Disabled or placeholder text

# Status Badges
STATUS_COLORS = {
    "Available": ACCENT_GREEN,
    "In Consultation": ACCENT_AMBER,
    "In Surgery": ACCENT_DANGER,
    "Off Duty": COLOR_TEXT_MUTED,
    "Scheduled": ACCENT_CYAN,
    "Completed": ACCENT_GREEN,
    "Cancelled": ACCENT_DANGER,
    "In Progress": ACCENT_AMBER,
    "Paid": ACCENT_GREEN,
    "Pending": ACCENT_AMBER,
    "Overdue": ACCENT_DANGER,
    "Active": ACCENT_GREEN,
    "Inactive": COLOR_TEXT_MUTED,
}

# --- TYPOGRAPHY CONSTANTS ---
# Standard Windows cross-platform safe fonts
FONT_FAMILY_TITLE = "Segoe UI"
FONT_FAMILY_BODY = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"

FONT_HERO = (FONT_FAMILY_TITLE, 22, "bold")
FONT_TITLE = (FONT_FAMILY_TITLE, 16, "bold")
FONT_SUBTITLE = (FONT_FAMILY_TITLE, 13, "bold")
FONT_CARD_VALUE = (FONT_FAMILY_TITLE, 20, "bold")
FONT_CARD_LABEL = (FONT_FAMILY_BODY, 10, "bold")
FONT_BODY = (FONT_FAMILY_BODY, 10)
FONT_BODY_BOLD = (FONT_FAMILY_BODY, 10, "bold")
FONT_SMALL = (FONT_FAMILY_BODY, 9)
FONT_MONO = (FONT_FAMILY_MONO, 9)
FONT_MONO_BOLD = (FONT_FAMILY_MONO, 9, "bold")
FONT_CLOCK = (FONT_FAMILY_MONO, 14, "bold")

# --- USER ROLES & PERMISSIONS ---
ROLE_ADMIN = "Admin"
ROLE_DOCTOR = "Doctor"
ROLE_RECEPTIONIST = "Receptionist"

ALL_ROLES = [ROLE_ADMIN, ROLE_DOCTOR, ROLE_RECEPTIONIST]

# Navigation modules accessible per role
ROLE_PERMISSIONS = {
    ROLE_ADMIN: [
        "dashboard",
        "patients",
        "doctors",
        "appointments",
        "medical_history",
        "billing",
        "analytics",
    ],
    ROLE_DOCTOR: [
        "dashboard",
        "patients",
        "appointments",
        "medical_history",
        "analytics",
    ],
    ROLE_RECEPTIONIST: [
        "dashboard",
        "patients",
        "doctors",
        "appointments",
        "billing",
    ],
}

# --- HOSPITAL SPECIALIZATIONS ---
MEDICAL_SPECIALIZATIONS = [
    "Neuro-Surgery & AI Brain Mapping",
    "Cardiovascular & Thoracic Surgery",
    "Internal Medicine & Diagnostics",
    "Orthopedic Surgery & Bio-prosthetics",
    "Pediatrics & Child Health",
    "Oncology & Cellular Therapy",
    "Dermatology & Laser Medicine",
    "Trauma & Emergency Care",
    "Ophthalmology & Robotic Optics",
    "General Surgery & Laparoscopy",
]

# Time slots for appointment bookings
APPOINTMENT_TIME_SLOTS = [
    "09:00 AM",
    "09:30 AM",
    "10:00 AM",
    "10:30 AM",
    "11:00 AM",
    "11:30 AM",
    "01:00 PM",
    "01:30 PM",
    "02:00 PM",
    "02:30 PM",
    "03:00 PM",
    "03:30 PM",
    "04:00 PM",
    "04:30 PM",
    "05:00 PM",
]
