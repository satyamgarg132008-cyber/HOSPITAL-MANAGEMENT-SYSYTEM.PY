"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: gui.py
Description: Master application shell featuring Tony Stark J.A.R.V.I.S.-inspired
             holographic user interface, live digital clock, animated sidebar
             navigation, role-based module filtering, and dynamic view switching.
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from security import current_session
from database import db
from voice_engine import voice_assistant

# Import all module views
from dashboard import DashboardView, AnimatedAICore
from patient_management import PatientManagementView
from doctor_management import DoctorManagementView
from appointment_management import AppointmentManagementView
from billing import BillingManagementView
from medical_history import MedicalHistoryView
from analytics import AnalyticsDashboardView


class MainWindow(tk.Tk):
    """
    Main Application Window for MEDNOVA AI.
    """

    def __init__(self):
        super().__init__()

        self.title(f"{config.APP_NAME} — {config.APP_SUBTITLE} [{config.APP_VERSION}]")
        self.geometry(f"{config.WINDOW_DEFAULT_WIDTH}x{config.WINDOW_DEFAULT_HEIGHT}")
        self.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        self.configure(bg=config.BG_DARK)

        # Center on desktop
        self._center_window(config.WINDOW_DEFAULT_WIDTH, config.WINDOW_DEFAULT_HEIGHT)

        # Apply dark ttk styling
        self._setup_ttk_styles()

        # State tracking
        self.current_view_name = None
        self.active_view = None
        self.nav_buttons = {}

        # Build primary UI shell
        self._build_topbar()
        self._build_layout()
        self._start_digital_clock()

    def _center_window(self, width, height):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_ttk_styles(self):
        """Configure high-tech dark theme for all native ttk widgets."""
        style = ttk.Style(self)
        style.theme_use("clam")

        # Treeview styling
        style.configure(
            "Treeview",
            background=config.BG_CARD,
            foreground=config.COLOR_TEXT_PRIMARY,
            fieldbackground=config.BG_CARD,
            font=config.FONT_BODY,
            rowheight=30,
            borderwidth=0
        )
        style.map(
            "Treeview",
            background=[("selected", "#004766")],
            foreground=[("selected", config.ACCENT_CYAN)]
        )

        # Treeview Header styling
        style.configure(
            "Treeview.Heading",
            background="#091428",
            foreground=config.ACCENT_CYAN,
            font=config.FONT_CARD_LABEL,
            borderwidth=1,
            relief="flat",
            padding=6
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#0F2347")],
            foreground=[("active", config.COLOR_TEXT_PRIMARY)]
        )

        # Combobox styling
        style.configure(
            "TCombobox",
            fieldbackground=config.BG_INPUT,
            background="#0B1A33",
            foreground=config.COLOR_TEXT_PRIMARY,
            darkcolor=config.ACCENT_BORDER,
            lightcolor=config.ACCENT_BORDER,
            arrowcolor=config.ACCENT_CYAN,
            font=config.FONT_BODY
        )

        # Scrollbar styling
        style.configure(
            "Vertical.TScrollbar",
            background="#0A152C",
            troughcolor=config.BG_DARK,
            bordercolor=config.ACCENT_BORDER,
            arrowcolor=config.ACCENT_CYAN
        )

    def _build_topbar(self):
        """Futuristic holographic top navigation header."""
        self.topbar = tk.Frame(self, bg=config.BG_PANEL, height=64, highlightthickness=1, highlightbackground=config.ACCENT_BORDER)
        self.topbar.pack(fill=tk.X, side=tk.TOP)
        self.topbar.pack_propagate(False)

        # Left: App Brand & Arc Reactor Core Logo
        brand_frame = tk.Frame(self.topbar, bg=config.BG_PANEL)
        brand_frame.pack(side=tk.LEFT, padx=16, fill=tk.Y)

        lbl_logo = tk.Label(
            brand_frame,
            text="◈ MEDNOVA AI",
            font=config.FONT_HERO,
            fg=config.ACCENT_CYAN,
            bg=config.BG_PANEL
        )
        lbl_logo.pack(side=tk.LEFT, pady=10)

        # Subtitle badge
        lbl_badge = tk.Label(
            brand_frame,
            text="SYSTEM ONLINE // QUANTUM CORE ACTIVE",
            font=config.FONT_MONO,
            fg=config.ACCENT_GREEN,
            bg="#06221A",
            padx=8,
            pady=3,
            relief=tk.FLAT
        )
        lbl_badge.pack(side=tk.LEFT, padx=(14, 0))

        # Right: User Profile, Live Clock, Voice Toggle, Logout
        right_frame = tk.Frame(self.topbar, bg=config.BG_PANEL)
        right_frame.pack(side=tk.RIGHT, padx=16, fill=tk.Y)

        # Live Digital Clock
        self.lbl_clock = tk.Label(
            right_frame,
            text="00:00:00 AM",
            font=config.FONT_CLOCK,
            fg=config.ACCENT_CYAN,
            bg=config.BG_PANEL
        )
        self.lbl_clock.pack(side=tk.LEFT, padx=14)

        # Voice Assistant Audio Toggle Button
        self.btn_voice = tk.Button(
            right_frame,
            text="🔊 VOICE: ON",
            font=config.FONT_SMALL,
            bg="#0D2C3D",
            fg=config.ACCENT_CYAN,
            activebackground=config.ACCENT_CYAN,
            activeforeground="#050814",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=4,
            command=self._toggle_voice
        )
        self.btn_voice.pack(side=tk.LEFT, padx=8)

        # Logged-in Staff Badge
        role_color = config.ACCENT_CYAN if current_session.role == config.ROLE_ADMIN else config.ACCENT_GREEN
        user_info = f"👤 {current_session.full_name} [{current_session.role.upper()}]"
        self.lbl_user = tk.Label(
            right_frame,
            text=user_info,
            font=config.FONT_BODY_BOLD,
            fg=role_color,
            bg="#0A1C36",
            padx=10,
            pady=4
        )
        self.lbl_user.pack(side=tk.LEFT, padx=8)

        # Logout Button
        self.btn_logout = tk.Button(
            right_frame,
            text="⏻ LOGOUT",
            font=config.FONT_SMALL,
            bg="#3B0D18",
            fg=config.ACCENT_DANGER,
            activebackground=config.ACCENT_DANGER,
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=4,
            command=self._confirm_logout
        )
        self.btn_logout.pack(side=tk.LEFT, padx=6)

    def _build_layout(self):
        """Construct sidebar and central dynamic workspace."""
        self.layout_frame = tk.Frame(self, bg=config.BG_DARK)
        self.layout_frame.pack(fill=tk.BOTH, expand=True)

        # Left Sidebar Frame
        self.sidebar = tk.Frame(self.layout_frame, bg=config.BG_PANEL, width=240, highlightthickness=1, highlightbackground=config.ACCENT_BORDER)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Sidebar Title
        lbl_nav_title = tk.Label(
            self.sidebar,
            text="COMMAND MODULES",
            font=config.FONT_CARD_LABEL,
            fg=config.COLOR_TEXT_SECONDARY,
            bg=config.BG_PANEL
        )
        lbl_nav_title.pack(anchor=tk.W, padx=18, pady=(16, 10))

        # Navigation Buttons list
        modules = [
            ("dashboard", "⬡ DASHBOARD", "Overview & AI core metrics"),
            ("patients", "⬡ PATIENT REGISTRY", "Demographics & census"),
            ("doctors", "⬡ PHYSICIAN ROSTER", "Specialists & schedules"),
            ("appointments", "⬡ APPOINTMENTS", "Bookings & conflict engine"),
            ("medical_history", "⬡ MEDICAL ARCHIVE", "Clinical notes & EHR"),
            ("billing", "⬡ BILLING & INVOICES", "Financial ledger & receipts"),
            ("analytics", "⬡ VISUAL ANALYTICS", "Canvas charts & telemetry"),
        ]

        # Filter navigation by logged in user's role permissions
        for mod_id, title, desc in modules:
            if current_session.has_permission(mod_id):
                btn = self._create_sidebar_button(self.sidebar, mod_id, title)
                btn.pack(fill=tk.X, padx=10, pady=3)
                self.nav_buttons[mod_id] = btn

        # Mini Animated Arc Reactor Core in sidebar bottom
        core_box = tk.Frame(self.sidebar, bg=config.BG_PANEL)
        core_box.pack(side=tk.BOTTOM, fill=tk.X, pady=16)

        self.sidebar_ai = AnimatedAICore(core_box, size=140)
        self.sidebar_ai.pack(pady=4)

        lbl_core_sub = tk.Label(
            core_box,
            text="J.A.R.V.I.S. QUANTUM V3.8\nSTATUS: ONLINE",
            font=config.FONT_MONO,
            fg=config.COLOR_TEXT_SECONDARY,
            bg=config.BG_PANEL,
            justify=tk.CENTER
        )
        lbl_core_sub.pack()

        # Right Dynamic Container
        self.main_content = tk.Frame(self.layout_frame, bg=config.BG_DARK)
        self.main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Global Bottom Status Footer
        self.footer = tk.Frame(self, bg="#03060E", height=28, highlightthickness=1, highlightbackground=config.ACCENT_BORDER)
        self.footer.pack(side=tk.BOTTOM, fill=tk.X)
        self.footer.pack_propagate(False)

        lbl_footer_info = tk.Label(
            self.footer,
            text="STATUS: ALL SYSTEMS SYNCHRONIZED   •   DATABASE: SQLITE3 WAL   •   SECURITY: SHA-256 ENCRYPTED",
            font=config.FONT_SMALL,
            fg=config.COLOR_TEXT_MUTED,
            bg="#03060E"
        )
        lbl_footer_info.pack(side=tk.LEFT, padx=16, pady=4)

        lbl_copy = tk.Label(
            self.footer,
            text=config.COPYRIGHT_TEXT,
            font=config.FONT_SMALL,
            fg=config.COLOR_TEXT_MUTED,
            bg="#03060E"
        )
        lbl_copy.pack(side=tk.RIGHT, padx=16, pady=4)

    def _create_sidebar_button(self, parent, module_id: str, title: str) -> tk.Button:
        """Create sleek cyber-styled navigation button with active state handling."""
        btn = tk.Button(
            parent,
            text=title,
            font=config.FONT_BODY_BOLD,
            bg=config.BG_PANEL,
            fg=config.COLOR_TEXT_SECONDARY,
            activebackground="#0E2345",
            activeforeground=config.ACCENT_CYAN,
            relief=tk.FLAT,
            bd=0,
            anchor=tk.W,
            padx=14,
            pady=10,
            cursor="hand2",
            command=lambda m=module_id: self.navigate_to(m)
        )

        def on_enter(e):
            if self.current_view_name != module_id:
                btn.configure(bg="#0C1B33", fg=config.COLOR_TEXT_PRIMARY)

        def on_leave(e):
            if self.current_view_name != module_id:
                btn.configure(bg=config.BG_PANEL, fg=config.COLOR_TEXT_SECONDARY)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def navigate_to(self, view_name: str, **kwargs):
        """
        Dynamically switch active module view in the main container.
        """
        if not current_session.has_permission(view_name):
            messagebox.showwarning("Access Restricted", f"Your role ({current_session.role}) does not have clearance for this module.")
            return

        # Destroy existing view
        if self.active_view is not None:
            self.active_view.destroy()
            self.active_view = None

        self.current_view_name = view_name

        # Update button highlights
        for mod_id, btn in self.nav_buttons.items():
            if mod_id == view_name:
                btn.configure(bg="#0E2E52", fg=config.ACCENT_CYAN, highlightthickness=1, highlightbackground=config.ACCENT_CYAN)
            else:
                btn.configure(bg=config.BG_PANEL, fg=config.COLOR_TEXT_SECONDARY, highlightthickness=0)

        # Instantiate requested view
        if view_name == "dashboard":
            self.active_view = DashboardView(self.main_content, navigation_controller=self)
        elif view_name == "patients":
            self.active_view = PatientManagementView(self.main_content, navigation_controller=self)
        elif view_name == "doctors":
            self.active_view = DoctorManagementView(self.main_content, navigation_controller=self)
        elif view_name == "appointments":
            self.active_view = AppointmentManagementView(self.main_content, navigation_controller=self)
        elif view_name == "medical_history":
            initial_pat = kwargs.get("patient_id", None)
            self.active_view = MedicalHistoryView(self.main_content, navigation_controller=self, initial_patient_id=initial_pat)
        elif view_name == "billing":
            self.active_view = BillingManagementView(self.main_content, navigation_controller=self)
        elif view_name == "analytics":
            self.active_view = AnalyticsDashboardView(self.main_content, navigation_controller=self)

        if self.active_view:
            self.active_view.pack(fill=tk.BOTH, expand=True)

    def _start_digital_clock(self):
        """Update live digital clock every second."""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M:%S %p")
        date_str = now.strftime("%a, %d %b %Y").upper()
        self.lbl_clock.configure(text=f"{date_str}  •  {time_str}")
        self.after(1000, self._start_digital_clock)

    def _toggle_voice(self):
        """Toggle offline pyttsx3 voice engine state."""
        new_state = voice_assistant.toggle()
        if new_state:
            self.btn_voice.configure(text="🔊 VOICE: ON", bg="#0D2C3D", fg=config.ACCENT_CYAN)
            voice_assistant.speak("Voice guidance system online.")
        else:
            self.btn_voice.configure(text="🔇 VOICE: MUTED", bg="#2B151A", fg=config.ACCENT_DANGER)

    def _confirm_logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to end your session and disconnect from the mainframe?")
        if confirm:
            db.log_activity(current_session.user_id, "LOGOUT", f"User {current_session.username} logged out.")
            current_session.clear()
            self.destroy()

            # Re-launch entry point login
            import main
            main.main()
