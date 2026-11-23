"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: analytics.py
Description: Executive visual analytics dashboard rendered natively on Tkinter
             Canvas. Features holographic cyber bar charts, appointment status
             doughnut plots, department workload metrics, and revenue trajectories.
=============================================================================
"""

import math
import tkinter as tk
from tkinter import ttk
import config
from database import db
from utils import GlowingButton, create_holographic_card, format_currency


class AnalyticsDashboardView(tk.Frame):
    """
    Holographic Canvas Visual Analytics Screen.
    """

    def __init__(self, parent, navigation_controller):
        super().__init__(parent, bg=config.BG_DARK)
        self.nav = navigation_controller

        self._build_ui()
        self.render_all_charts()

    def _build_ui(self):
        self.main_container = tk.Frame(self, bg=config.BG_DARK)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # Header Control Bar
        header_card = create_holographic_card(self.main_container, title="HOSPITAL ANALYTICS & TELEMETRY MAINFRAME", subtitle="CANVAS NEURAL PLOTTING")
        header_card.pack(fill=tk.X, pady=(0, 14))

        ctrl_frame = tk.Frame(header_card, bg=config.BG_CARD)
        ctrl_frame.pack(fill=tk.X, padx=14, pady=10)

        lbl_info = tk.Label(
            ctrl_frame,
            text="REAL-TIME SQLITE DATA VISUALIZATION ENGINE • 100% NATIVE TKINTER CANVAS",
            font=config.FONT_CARD_LABEL,
            fg=config.COLOR_TEXT_CYAN,
            bg=config.BG_CARD
        )
        lbl_info.pack(side=tk.LEFT)

        btn_refresh = GlowingButton(ctrl_frame, text="↻ RECALCULATE TELEMETRY", theme="cyan", command=self.render_all_charts)
        btn_refresh.pack(side=tk.RIGHT)

        # 2x2 Grid Container for 4 Futuristic Charts
        grid_container = tk.Frame(self.main_container, bg=config.BG_DARK)
        grid_container.pack(fill=tk.BOTH, expand=True)

        grid_container.columnconfigure(0, weight=1)
        grid_container.columnconfigure(1, weight=1)
        grid_container.rowconfigure(0, weight=1)
        grid_container.rowconfigure(1, weight=1)

        # Chart 1: Monthly Patient Census (Bar Chart)
        c1_card = create_holographic_card(grid_container, title="MONTHLY PATIENT ADMISSIONS", subtitle="ANNUAL CENSUS")
        c1_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        self.canvas_monthly = tk.Canvas(c1_card, bg=config.BG_CARD, bd=0, highlightthickness=0)
        self.canvas_monthly.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        # Chart 2: Appointment Status Distribution (Donut Chart)
        c2_card = create_holographic_card(grid_container, title="APPOINTMENTS BREAKDOWN", subtitle="STATUS DISTRIBUTION")
        c2_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
        self.canvas_donut = tk.Canvas(c2_card, bg=config.BG_CARD, bd=0, highlightthickness=0)
        self.canvas_donut.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        # Chart 3: Hospital Revenue Trajectory (Line / Node Chart)
        c3_card = create_holographic_card(grid_container, title="REVENUE LEDGER TRAJECTORY", subtitle="SETTLED INVOICES")
        c3_card.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(8, 0))
        self.canvas_revenue = tk.Canvas(c3_card, bg=config.BG_CARD, bd=0, highlightthickness=0)
        self.canvas_revenue.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        # Chart 4: Department / Specialist Workload (Horizontal Bar Chart)
        c4_card = create_holographic_card(grid_container, title="DEPARTMENTAL CASELOAD", subtitle="TOP SPECIALIZATIONS")
        c4_card.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(8, 0))
        self.canvas_workload = tk.Canvas(c4_card, bg=config.BG_CARD, bd=0, highlightthickness=0)
        self.canvas_workload.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

    def render_all_charts(self):
        """Redraw all 4 canvas graphs using fresh data from SQLite."""
        self.update_idletasks()
        self._draw_monthly_bars()
        self._draw_status_donut()
        self._draw_revenue_line()
        self._draw_workload_bars()

    # =========================================================================
    # CHART 1: MONTHLY PATIENT ADMISSIONS (BAR CHART)
    # =========================================================================
    def _draw_monthly_bars(self):
        c = self.canvas_monthly
        c.delete("all")
        w = c.winfo_width() or 400
        h = c.winfo_height() or 200

        data = db.get_monthly_patient_admissions()  # List of ('Jan', count), ...
        if not data:
            return

        pad_left, pad_bottom, pad_top, pad_right = 45, 30, 25, 20
        plot_w = w - pad_left - pad_right
        plot_h = h - pad_top - pad_bottom

        # Grid lines and baseline
        c.create_line(pad_left, h - pad_bottom, w - pad_right, h - pad_bottom, fill=config.ACCENT_BORDER, width=1)
        c.create_line(pad_left, pad_top, pad_left, h - pad_bottom, fill=config.ACCENT_BORDER, width=1)

        counts = [val for _, val in data]
        max_val = max(counts) if max(counts) > 0 else 5
        # Round max_val up to clean ceiling
        max_ceil = max(5, int(math.ceil(max_val * 1.2)))

        # Y-axis ticks
        for i in range(4):
            y_val = int(max_ceil * (i / 3))
            y_pos = (h - pad_bottom) - (plot_h * (i / 3))
            c.create_text(pad_left - 10, y_pos, text=str(y_val), font=config.FONT_SMALL, fill=config.COLOR_TEXT_MUTED, anchor=tk.E)
            c.create_line(pad_left, y_pos, w - pad_right, y_pos, fill="#0A1830", width=1, dash=(4, 4))

        # Bars
        num_bars = len(data)
        bar_slot = plot_w / num_bars
        bar_width = max(10, bar_slot * 0.6)

        for idx, (month, count) in enumerate(data):
            x_center = pad_left + (idx * bar_slot) + (bar_slot / 2)
            bar_height = (count / max_ceil) * plot_h
            y_top = (h - pad_bottom) - bar_height
            y_bottom = h - pad_bottom

            x0 = x_center - (bar_width / 2)
            x1 = x_center + (bar_width / 2)

            # Holographic bar with cyan neon glow
            fill_col = config.ACCENT_CYAN if count > 0 else "#0D223A"
            outline_col = config.ACCENT_CYAN if count > 0 else config.ACCENT_BORDER

            c.create_rectangle(x0, y_top, x1, y_bottom, fill=fill_col, outline=outline_col, width=1)

            # Value label atop bar
            if count > 0:
                c.create_text(x_center, y_top - 8, text=str(count), font=config.FONT_SMALL, fill=config.ACCENT_CYAN)

            # X-axis Month Label
            c.create_text(x_center, h - pad_bottom + 14, text=month, font=config.FONT_SMALL, fill=config.COLOR_TEXT_SECONDARY)

    # =========================================================================
    # CHART 2: APPOINTMENT STATUS DOUGHNUT CHART
    # =========================================================================
    def _draw_status_donut(self):
        c = self.canvas_donut
        c.delete("all")
        w = c.winfo_width() or 400
        h = c.winfo_height() or 200

        data = db.get_appointment_status_distribution()
        total_apts = sum(data.values())

        cx = w * 0.35
        cy = h * 0.50
        r_outer = min(cx, cy) * 0.75
        r_inner = r_outer * 0.55

        colors = {
            "Scheduled": config.ACCENT_CYAN,
            "Completed": config.ACCENT_GREEN,
            "In Progress": config.ACCENT_AMBER,
            "Cancelled": config.ACCENT_DANGER,
        }

        if total_apts == 0:
            c.create_oval(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer, outline=config.ACCENT_BORDER, width=2)
            c.create_text(cx, cy, text="NO DATA", font=config.FONT_BODY, fill=config.COLOR_TEXT_MUTED)
            return

        current_angle = 90
        for status, count in data.items():
            if count <= 0:
                continue
            extent = (count / total_apts) * 360
            c.create_arc(
                cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer,
                start=current_angle, extent=extent,
                fill=colors.get(status, config.ACCENT_CYAN),
                outline=config.BG_CARD,
                width=2
            )
            current_angle += extent

        # Inner cut-out circle to create Doughnut effect
        c.create_oval(cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner, fill=config.BG_CARD, outline=config.ACCENT_BORDER, width=1)
        c.create_text(cx, cy - 6, text=str(total_apts), font=config.FONT_HERO, fill=config.COLOR_TEXT_PRIMARY)
        c.create_text(cx, cy + 12, text="TOTAL", font=config.FONT_CARD_LABEL, fill=config.COLOR_TEXT_SECONDARY)

        # Legend on the right side
        lx = w * 0.65
        ly = cy - 40
        for status, count in data.items():
            col = colors.get(status, config.ACCENT_CYAN)
            percent = (count / total_apts * 100) if total_apts > 0 else 0
            c.create_oval(lx, ly + 2, lx + 10, ly + 12, fill=col, outline="")
            c.create_text(lx + 18, ly + 6, text=f"{status}: {count} ({percent:.0f}%)", font=config.FONT_SMALL, fill=config.COLOR_TEXT_SECONDARY, anchor=tk.W)
            ly += 22

    # =========================================================================
    # CHART 3: REVENUE LEDGER TRAJECTORY (LINE / NODE CHART)
    # =========================================================================
    def _draw_revenue_line(self):
        c = self.canvas_revenue
        c.delete("all")
        w = c.winfo_width() or 400
        h = c.winfo_height() or 200

        data = db.get_revenue_timeline()
        if not data:
            return

        pad_left, pad_bottom, pad_top, pad_right = 65, 30, 25, 20
        plot_w = w - pad_left - pad_right
        plot_h = h - pad_top - pad_bottom

        # Grid lines
        c.create_line(pad_left, h - pad_bottom, w - pad_right, h - pad_bottom, fill=config.ACCENT_BORDER, width=1)
        c.create_line(pad_left, pad_top, pad_left, h - pad_bottom, fill=config.ACCENT_BORDER, width=1)

        amounts = [amt for _, amt in data]
        max_amt = max(amounts) if max(amounts) > 0 else 1000.0
        max_ceil = max(1000.0, float(math.ceil(max_amt * 1.25)))

        # Y-axis ticks
        for i in range(4):
            val = max_ceil * (i / 3)
            y_pos = (h - pad_bottom) - (plot_h * (i / 3))
            c.create_text(pad_left - 8, y_pos, text=format_currency(val), font=config.FONT_SMALL, fill=config.COLOR_TEXT_MUTED, anchor=tk.E)
            c.create_line(pad_left, y_pos, w - pad_right, y_pos, fill="#0A1830", width=1, dash=(4, 4))

        # Calculate points
        points = []
        n = len(data)
        dx = plot_w / (n - 1) if n > 1 else plot_w / 2

        for idx, (dt_label, amt) in enumerate(data):
            x = pad_left + (idx * dx) if n > 1 else pad_left + (plot_w / 2)
            y = (h - pad_bottom) - ((amt / max_ceil) * plot_h)
            points.append((x, y, dt_label, amt))

        # Draw connecting line segments
        for i in range(len(points) - 1):
            x1, y1, _, _ = points[i]
            x2, y2, _, _ = points[i + 1]
            c.create_line(x1, y1, x2, y2, fill=config.ACCENT_BLUE, width=3)

        # Draw glowing data nodes and labels
        for x, y, dt_label, amt in points:
            c.create_oval(x - 5, y - 5, x + 5, y + 5, fill=config.BG_CARD, outline=config.ACCENT_CYAN, width=2)
            c.create_oval(x - 2, y - 2, x + 2, y + 2, fill=config.ACCENT_GREEN, outline="")
            c.create_text(x, y - 10, text=format_currency(amt), font=config.FONT_SMALL, fill=config.ACCENT_CYAN)

            # Date snippet label on X axis
            short_date = dt_label[-5:] if len(dt_label) >= 5 else dt_label
            c.create_text(x, h - pad_bottom + 14, text=short_date, font=config.FONT_SMALL, fill=config.COLOR_TEXT_SECONDARY)

    # =========================================================================
    # CHART 4: DEPARTMENT WORKLOAD (HORIZONTAL BAR CHART)
    # =========================================================================
    def _draw_workload_bars(self):
        c = self.canvas_workload
        c.delete("all")
        w = c.winfo_width() or 400
        h = c.winfo_height() or 200

        data = db.get_doctor_workload_distribution()
        if not data:
            return

        pad_left, pad_bottom, pad_top, pad_right = 160, 20, 20, 45
        plot_w = w - pad_left - pad_right
        plot_h = h - pad_top - pad_bottom

        counts = [cnt for _, cnt in data]
        max_cnt = max(counts) if max(counts) > 0 else 5

        num_items = len(data)
        slot_h = plot_h / num_items
        bar_h = min(22, slot_h * 0.65)

        for idx, (spec_name, count) in enumerate(data):
            y_center = pad_top + (idx * slot_h) + (slot_h / 2)
            bar_len = (count / max_cnt) * plot_w if max_cnt > 0 else 0

            # Department text label (truncated if long)
            display_name = spec_name if len(spec_name) < 22 else spec_name[:20] + ".."
            c.create_text(pad_left - 10, y_center, text=display_name, font=config.FONT_SMALL, fill=config.COLOR_TEXT_SECONDARY, anchor=tk.E)

            # Horizontal Bar
            x0 = pad_left
            y0 = y_center - (bar_h / 2)
            x1 = pad_left + bar_len
            y1 = y_center + (bar_h / 2)

            bar_color = config.ACCENT_PURPLE if idx % 2 == 0 else config.ACCENT_CYAN
            c.create_rectangle(x0, y0, x1, y1, fill=bar_color, outline=config.ACCENT_BORDER, width=1)

            # Count number label
            c.create_text(x1 + 14, y_center, text=f"{count} cases", font=config.FONT_SMALL, fill=config.COLOR_TEXT_PRIMARY, anchor=tk.W)
