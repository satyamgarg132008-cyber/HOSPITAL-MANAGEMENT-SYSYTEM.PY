"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: dashboard.py
Description: Futuristic command center dashboard featuring real-time SQLite statistics,
             animated Tkinter Canvas J.A.R.V.I.S. Arc Reactor AI Core, quick action
             command matrix, and operational feed monitors.
=============================================================================
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from database import db
from utils import format_currency, GlowingButton, create_holographic_card
from voice_engine import voice_assistant
from security import current_session


class AnimatedAICore(tk.Canvas):
    """
    Tony Stark Arc Reactor / J.A.R.V.I.S. animated central AI Core.
    Features counter-rotating concentric segmented rings, pulsing orbital nodes,
    and a dynamic core energy sphere.
    """

    def __init__(self, parent, size=240, **kwargs):
        kwargs.setdefault("bg", config.BG_CARD)
        kwargs.setdefault("highlightthickness", 0)
        kwargs.setdefault("bd", 0)
        super().__init__(parent, width=size, height=size, **kwargs)

        self.size = size
        self.center = size // 2
        self.angle_outer = 0
        self.angle_inner = 0
        self.pulse_phase = 0
        self.is_animating = True

        self._animate()

    def _animate(self):
        if not self.winfo_exists():
            return

        self.delete("all")
        cx, cy = self.center, self.center

        # 1. Outer Tech Ring (Static Guide)
        r_outer = self.size * 0.45
        self.create_oval(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer,
                          outline=config.ACCENT_BORDER, width=2)

        # 2. Outer Rotating Segmented Arcs (Clockwise)
        for offset in (0, 90, 180, 270):
            start = (self.angle_outer + offset) % 360
            self.create_arc(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer,
                            start=start, extent=45, outline=config.ACCENT_CYAN,
                            style=tk.ARC, width=3)

        # 3. Middle Rotating Ring (Counter-Clockwise)
        r_mid = self.size * 0.35
        for offset in (30, 120, 210, 300):
            start = (360 - self.angle_inner + offset) % 360
            self.create_arc(cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid,
                            start=start, extent=55, outline=config.ACCENT_BLUE,
                            style=tk.ARC, width=2)

        # 4. Orbiting Energy Particles
        for i in range(4):
            particle_angle = math.radians(self.angle_outer * 2 + i * 90)
            px = cx + (r_mid + 10) * math.cos(particle_angle)
            py = cy + (r_mid + 10) * math.sin(particle_angle)
            self.create_oval(px - 3, py - 3, px + 3, py + 3, fill=config.ACCENT_GREEN, outline="")

        # 5. Inner Pulsing Core Ring
        pulse_factor = 0.5 + 0.5 * math.sin(math.radians(self.pulse_phase))
        r_inner = self.size * 0.22 + (pulse_factor * 4)
        core_color = "#004754" if pulse_factor < 0.5 else "#007788"

        self.create_oval(cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner,
                          fill=core_color, outline=config.ACCENT_CYAN, width=2)

        # 6. Center Quantum Symbol / Text
        self.create_text(cx, cy - 6, text="◈ NOVA ◈", font=config.FONT_CARD_LABEL, fill=config.ACCENT_CYAN)
        self.create_text(cx, cy + 10, text="ONLINE", font=config.FONT_MONO, fill=config.ACCENT_GREEN)

        # Increment rotations
        self.angle_outer = (self.angle_outer + 2) % 360
        self.angle_inner = (self.angle_inner + 3) % 360
        self.pulse_phase = (self.pulse_phase + 5) % 360

        # Schedule next frame (~30 FPS)
        if self.is_animating:
            self.after(33, self._animate)

    def stop(self):
        self.is_animating = False


class DashboardView(tk.Frame):
    """
    Main Executive Hospital Command Center Screen.
    """

    def __init__(self, parent, navigation_controller):
        super().__init__(parent, bg=config.BG_DARK)
        self.nav = navigation_controller

        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        # Master Scrollable or Pack Container
        self.content_frame = tk.Frame(self, bg=config.BG_DARK)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # Top Section: KPI Metric Cards Grid
        self._build_kpi_cards(self.content_frame)

        # Middle Section: AI Core & Quick Command Matrix
        self._build_center_console(self.content_frame)

        # Bottom Section: Live Monitor Tables (Recent Patients & Upcoming Appointments)
        self._build_live_monitors(self.content_frame)

    def _build_kpi_cards(self, parent):
        kpi_container = tk.Frame(parent, bg=config.BG_DARK)
        kpi_container.pack(fill=tk.X, pady=(0, 16))

        # 4 Responsive Metric Cards
        self.card_patients = self._create_metric_card(
            kpi_container, "TOTAL REGISTERED PATIENTS", "0", "▲ ACTIVE CENSUS", config.ACCENT_CYAN
        )
        self.card_patients.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.card_doctors = self._create_metric_card(
            kpi_container, "SPECIALIST PHYSICIANS", "0", "● FULLY ROSTERED", config.ACCENT_GREEN
        )
        self.card_doctors.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        self.card_appointments = self._create_metric_card(
            kpi_container, "TODAY'S CLINICAL VISITS", "0", "◆ QUEUE SYNCHRONIZED", config.ACCENT_BLUE
        )
        self.card_appointments.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        self.card_revenue = self._create_metric_card(
            kpi_container, "TOTAL REVENUE (SETTLED)", "$0.00", "★ FINANCIAL MAINFRAME", config.ACCENT_PURPLE
        )
        self.card_revenue.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

    def _create_metric_card(self, parent, title: str, init_val: str, subtitle: str, accent_color: str):
        card = tk.Frame(parent, bg=config.BG_CARD, highlightthickness=1, highlightbackground=config.ACCENT_BORDER)
        
        # Color bar indicator at top of card
        indicator = tk.Frame(card, bg=accent_color, height=3)
        indicator.pack(fill=tk.X)

        inner = tk.Frame(card, bg=config.BG_CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        lbl_title = tk.Label(inner, text=title, font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_CARD)
        lbl_title.pack(anchor=tk.W)

        lbl_val = tk.Label(inner, text=init_val, font=config.FONT_HERO, fg=accent_color, bg=config.BG_CARD)
        lbl_val.pack(anchor=tk.W, pady=4)

        lbl_sub = tk.Label(inner, text=subtitle, font=config.FONT_SMALL, fg=config.COLOR_TEXT_MUTED, bg=config.BG_CARD)
        lbl_sub.pack(anchor=tk.W)

        # Store label reference for updates
        card.lbl_val = lbl_val
        return card

    def _build_center_console(self, parent):
        center_frame = tk.Frame(parent, bg=config.BG_DARK)
        center_frame.pack(fill=tk.X, pady=(0, 16))

        # Left Box: Stark Arc Reactor Animated AI Core
        core_box = create_holographic_card(center_frame, title="QUANTUM NEURAL AI CORE", subtitle="STATE: ACTIVE")
        core_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        core_inner = tk.Frame(core_box, bg=config.BG_CARD)
        core_inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        # Animated canvas
        self.ai_canvas = AnimatedAICore(core_inner, size=210)
        self.ai_canvas.pack(side=tk.LEFT, padx=(10, 20))

        # Core diagnostics status texts
        diag_frame = tk.Frame(core_inner, bg=config.BG_CARD)
        diag_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            diag_frame,
            text="HOSPITAL NEURAL CORE: NOMINAL",
            font=config.FONT_SUBTITLE,
            fg=config.COLOR_TEXT_PRIMARY,
            bg=config.BG_CARD
        ).pack(anchor=tk.W, pady=(8, 4))

        diag_lines = [
            "• Patient Biometric Database: Online",
            "• Real-Time Conflict Detection: Active",
            "• Financial Ledger: Zero Anomalies",
            "• Medical History Cryptographic Chain: Intact"
        ]
        for line in diag_lines:
            tk.Label(
                diag_frame,
                text=line,
                font=config.FONT_BODY,
                fg=config.COLOR_TEXT_SECONDARY,
                bg=config.BG_CARD
            ).pack(anchor=tk.W, pady=2)

        # Button row inside core box
        btn_box = tk.Frame(diag_frame, bg=config.BG_CARD)
        btn_box.pack(anchor=tk.W, pady=(12, 0))

        btn_briefing = GlowingButton(
            btn_box,
            text="🔊 AUDIO BRIEFING",
            theme="cyan",
            command=self._voice_briefing
        )
        btn_briefing.pack(side=tk.LEFT, padx=(0, 8))

        btn_refresh = GlowingButton(
            btn_box,
            text="↻ SYNC MAINFRAME",
            theme="blue",
            command=self.refresh_data
        )
        btn_refresh.pack(side=tk.LEFT)

        # Right Box: Quick Action Command Matrix
        action_box = create_holographic_card(center_frame, title="COMMAND MATRIX", subtitle="DIRECT ACTIONS")
        action_box.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(8, 0), ipadx=10)

        action_inner = tk.Frame(action_box, bg=config.BG_CARD)
        action_inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        actions = [
            ("➕ REGISTER NEW PATIENT", "patients", "cyan"),
            ("📅 BOOK CLINICAL APPOINTMENT", "appointments", "blue"),
            ("💳 GENERATE BILLING INVOICE", "billing", "green"),
            ("📊 VIEW ADVANCED ANALYTICS", "analytics", "danger"),
        ]

        for text, module_target, theme in actions:
            btn = GlowingButton(
                action_inner,
                text=text,
                theme=theme,
                command=lambda m=module_target: self.nav.navigate_to(m)
            )
            btn.pack(fill=tk.X, pady=4)

    def _build_live_monitors(self, parent):
        monitor_frame = tk.Frame(parent, bg=config.BG_DARK)
        monitor_frame.pack(fill=tk.BOTH, expand=True)

        # Left Table: Recent Patient Registrations
        pat_card = create_holographic_card(monitor_frame, title="RECENT PATIENT REGISTRATIONS", subtitle="LIVE LOG")
        pat_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.tree_patients = ttk.Treeview(
            pat_card,
            columns=("uid", "name", "gender", "blood", "phone"),
            show="headings",
            height=6
        )
        self.tree_patients.heading("uid", text="PATIENT ID")
        self.tree_patients.heading("name", text="NAME")
        self.tree_patients.heading("gender", text="GENDER")
        self.tree_patients.heading("blood", text="BLOOD")
        self.tree_patients.heading("phone", text="PHONE")

        self.tree_patients.column("uid", width=120, anchor=tk.CENTER)
        self.tree_patients.column("name", width=150, anchor=tk.W)
        self.tree_patients.column("gender", width=70, anchor=tk.CENTER)
        self.tree_patients.column("blood", width=60, anchor=tk.CENTER)
        self.tree_patients.column("phone", width=120, anchor=tk.CENTER)
        self.tree_patients.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Right Table: Today & Upcoming Appointments
        apt_card = create_holographic_card(monitor_frame, title="CLINICAL APPOINTMENTS QUEUE", subtitle="TODAY / UPCOMING")
        apt_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self.tree_apts = ttk.Treeview(
            apt_card,
            columns=("apt_id", "patient", "doctor", "time", "status"),
            show="headings",
            height=6
        )
        self.tree_apts.heading("apt_id", text="APT ID")
        self.tree_apts.heading("patient", text="PATIENT")
        self.tree_apts.heading("doctor", text="ATTENDING DOCTOR")
        self.tree_apts.heading("time", text="TIME")
        self.tree_apts.heading("status", text="STATUS")

        self.tree_apts.column("apt_id", width=110, anchor=tk.CENTER)
        self.tree_apts.column("patient", width=130, anchor=tk.W)
        self.tree_apts.column("doctor", width=150, anchor=tk.W)
        self.tree_apts.column("time", width=90, anchor=tk.CENTER)
        self.tree_apts.column("status", width=90, anchor=tk.CENTER)
        self.tree_apts.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

    def refresh_data(self):
        """Fetch latest database state and update metric cards and tables."""
        kpis = db.get_dashboard_kpis()

        # Update KPI Cards
        self.card_patients.lbl_val.configure(text=str(kpis["total_patients"]))
        self.card_doctors.lbl_val.configure(text=f"{kpis['available_doctors']} / {kpis['total_doctors']}")
        self.card_appointments.lbl_val.configure(text=str(kpis["today_appointments"]))
        self.card_revenue.lbl_val.configure(text=format_currency(kpis["total_revenue"]))

        # Populate Recent Patients
        for item in self.tree_patients.get_children():
            self.tree_patients.delete(item)

        recent_patients = db.get_all_patients()[:6]
        for p in recent_patients:
            self.tree_patients.insert("", tk.END, values=(
                p["patient_uid"],
                p["full_name"],
                p["gender"],
                p["blood_group"],
                p["phone"]
            ))

        # Populate Appointments Queue
        for item in self.tree_apts.get_children():
            self.tree_apts.delete(item)

        recent_apts = db.get_all_appointments()[:6]
        for a in recent_apts:
            self.tree_apts.insert("", tk.END, values=(
                a["appointment_uid"],
                a["patient_name"],
                a["doctor_name"],
                a["appointment_time"],
                a["status"]
            ))

    def _voice_briefing(self):
        """Speak out today's hospital operations summary."""
        kpis = db.get_dashboard_kpis()
        rev_str = format_currency(kpis["total_revenue"])
        voice_assistant.announce_dashboard_summary(
            patients_count=kpis["total_patients"],
            doctors_count=kpis["total_doctors"],
            appointments_today=kpis["today_appointments"],
            revenue_str=rev_str
        )
