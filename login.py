"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: login.py
Description: Futuristic holographic biometric & credentials authentication portal.
             Supports multi-role authentication, password hashing verification,
             quick demo account presets, and animated canvas styling.
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import config
from security import verify_password, current_session
from database import db
from utils import GlowingButton
from voice_engine import voice_assistant


class LoginWindow(tk.Toplevel):
    """
    Futuristic Stark-themed login dialog window.
    """

    def __init__(self, parent, on_success_callback):
        super().__init__(parent)
        self.parent = parent
        self.on_success_callback = on_success_callback

        self.title("MEDNOVA AI — SECURITY ACCESS GATEWAY")
        self.geometry("880x620")
        self.minsize(800, 580)
        self.configure(bg=config.BG_DARK)
        self.resizable(False, False)

        # Center on screen
        self._center_window(880, 620)

        # Prevent closing master without login
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Password visibility state
        self.password_visible = False

        # Build UI layout
        self._build_ui()

    def _center_window(self, width, height):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        # Outer master frame with holographic cyan border
        outer_frame = tk.Frame(
            self,
            bg=config.BG_PANEL,
            highlightthickness=2,
            highlightbackground=config.ACCENT_CYAN
        )
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Top Futuristic Header Canvas
        header_canvas = tk.Canvas(outer_frame, height=90, bg=config.BG_DARK, bd=0, highlightthickness=0)
        header_canvas.pack(fill=tk.X)

        # Draw tech grid and title on canvas
        header_canvas.create_line(0, 88, 880, 88, fill=config.ACCENT_CYAN, width=2)
        header_canvas.create_text(
            440, 32,
            text="◈ MEDNOVA AI • SECURE ACCESS GATEWAY ◈",
            font=config.FONT_HERO,
            fill=config.ACCENT_CYAN
        )
        header_canvas.create_text(
            440, 64,
            text="HOSPITAL NEURAL MAINFRAME // LEVEL-7 BIOMETRIC VERIFICATION",
            font=config.FONT_MONO,
            fill=config.COLOR_TEXT_SECONDARY
        )

        # Main content two-column split
        content = tk.Frame(outer_frame, bg=config.BG_PANEL)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Left Column: Futuristic Arc / J.A.R.V.I.S. Core graphic & Security Status
        left_col = tk.Frame(content, bg=config.BG_CARD, width=320, highlightthickness=1, highlightbackground=config.ACCENT_BORDER)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 15))
        left_col.pack_propagate(False)

        self._draw_left_panel(left_col)

        # Right Column: Login Credentials Form
        right_col = tk.Frame(content, bg=config.BG_CARD, highlightthickness=1, highlightbackground=config.ACCENT_BORDER)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._draw_login_form(right_col)

        # Bottom Status Bar
        footer = tk.Frame(outer_frame, bg=config.BG_DARK, height=36)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        lbl_status = tk.Label(
            footer,
            text="SYSTEM INTEGRITY: 100% • ENCRYPTION: SHA-256 HMAC • STANDBY MODE",
            font=config.FONT_SMALL,
            fg=config.COLOR_TEXT_MUTED,
            bg=config.BG_DARK
        )
        lbl_status.pack(pady=6)

    def _draw_left_panel(self, parent):
        lbl = tk.Label(
            parent,
            text="NEURAL ACCESS SYSTEM",
            font=config.FONT_CARD_LABEL,
            fg=config.ACCENT_CYAN,
            bg=config.BG_CARD
        )
        lbl.pack(pady=(16, 8))

        # Mini Arc Reactor Graphic
        canvas_arc = tk.Canvas(parent, width=180, height=180, bg=config.BG_CARD, bd=0, highlightthickness=0)
        canvas_arc.pack(pady=10)

        # Draw concentric Stark rings
        canvas_arc.create_oval(15, 15, 165, 165, outline=config.ACCENT_BORDER, width=2)
        canvas_arc.create_oval(35, 35, 145, 145, outline=config.ACCENT_CYAN, width=2)
        canvas_arc.create_oval(55, 55, 125, 125, outline=config.ACCENT_BLUE, width=3, dash=(6, 4))
        canvas_arc.create_oval(70, 70, 110, 110, fill="#003547", outline=config.ACCENT_GREEN, width=2)
        canvas_arc.create_text(90, 90, text="CORE\nONLINE", font=config.FONT_MONO_BOLD, fill=config.ACCENT_CYAN, justify=tk.CENTER)

        # Instructions / Security notes
        info_text = (
            "Select role preset below\n"
            "or enter assigned staff\n"
            "credentials to access the\n"
            "command dashboard.\n\n"
            "Default Passwords:\n"
            "• Admin: admin123\n"
            "• Doctor: stark123\n"
            "• Receptionist: pepper123"
        )
        lbl_info = tk.Label(
            parent,
            text=info_text,
            font=config.FONT_MONO,
            fg=config.COLOR_TEXT_SECONDARY,
            bg=config.BG_CARD,
            justify=tk.LEFT
        )
        lbl_info.pack(pady=10, padx=16, anchor=tk.W)

    def _draw_login_form(self, parent):
        form_inner = tk.Frame(parent, bg=config.BG_CARD)
        form_inner.pack(fill=tk.BOTH, expand=True, padx=30, pady=24)

        lbl_header = tk.Label(
            form_inner,
            text="STAFF IDENTIFICATION PORTAL",
            font=config.FONT_SUBTITLE,
            fg=config.COLOR_TEXT_PRIMARY,
            bg=config.BG_CARD
        )
        lbl_header.pack(anchor=tk.W, pady=(0, 4))

        lbl_sub = tk.Label(
            form_inner,
            text="Provide authorized clearance credentials to initialize mainframe",
            font=config.FONT_SMALL,
            fg=config.COLOR_TEXT_SECONDARY,
            bg=config.BG_CARD
        )
        lbl_sub.pack(anchor=tk.W, pady=(0, 16))

        # Preset Role Auto-Fill Bar (Perfect for fast university viva evaluation!)
        preset_frame = tk.Frame(form_inner, bg=config.BG_CARD)
        preset_frame.pack(fill=tk.X, pady=(0, 16))

        lbl_preset = tk.Label(
            preset_frame,
            text="DEMO PRESETS:",
            font=config.FONT_CARD_LABEL,
            fg=config.COLOR_TEXT_CYAN,
            bg=config.BG_CARD
        )
        lbl_preset.pack(side=tk.LEFT, padx=(0, 8))

        btn_admin = tk.Button(
            preset_frame,
            text="[ADMIN]",
            font=config.FONT_SMALL,
            bg="#0D223A",
            fg=config.ACCENT_CYAN,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self._apply_preset("admin", "admin123")
        )
        btn_admin.pack(side=tk.LEFT, padx=3)

        btn_doc = tk.Button(
            preset_frame,
            text="[DOCTOR]",
            font=config.FONT_SMALL,
            bg="#0D223A",
            fg=config.ACCENT_GREEN,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self._apply_preset("dr_tony", "stark123")
        )
        btn_doc.pack(side=tk.LEFT, padx=3)

        btn_recep = tk.Button(
            preset_frame,
            text="[RECEPTION]",
            font=config.FONT_SMALL,
            bg="#0D223A",
            fg=config.ACCENT_PURPLE,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self._apply_preset("recep_pepper", "pepper123")
        )
        btn_recep.pack(side=tk.LEFT, padx=3)

        # Username Field
        lbl_user = tk.Label(
            form_inner,
            text="OPERATOR USERNAME",
            font=config.FONT_BODY_BOLD,
            fg=config.COLOR_TEXT_SECONDARY,
            bg=config.BG_CARD
        )
        lbl_user.pack(anchor=tk.W, pady=(4, 2))

        self.user_border = tk.Frame(form_inner, bg=config.ACCENT_BORDER, padx=1, pady=1)
        self.user_border.pack(fill=tk.X, pady=(0, 12))

        self.entry_user = tk.Entry(
            self.user_border,
            bg=config.BG_INPUT,
            fg=config.COLOR_TEXT_PRIMARY,
            insertbackground=config.ACCENT_CYAN,
            relief=tk.FLAT,
            font=config.FONT_BODY
        )
        self.entry_user.pack(fill=tk.X, ipady=8, padx=6)
        self.entry_user.insert(0, "admin")
        self.entry_user.bind("<FocusIn>", lambda e: self.user_border.configure(bg=config.ACCENT_CYAN))
        self.entry_user.bind("<FocusOut>", lambda e: self.user_border.configure(bg=config.ACCENT_BORDER))

        # Password Field
        lbl_pwd = tk.Label(
            form_inner,
            text="SECURITY ACCESS KEY (PASSWORD)",
            font=config.FONT_BODY_BOLD,
            fg=config.COLOR_TEXT_SECONDARY,
            bg=config.BG_CARD
        )
        lbl_pwd.pack(anchor=tk.W, pady=(4, 2))

        self.pwd_border = tk.Frame(form_inner, bg=config.ACCENT_BORDER, padx=1, pady=1)
        self.pwd_border.pack(fill=tk.X, pady=(0, 6))

        pwd_inner_frame = tk.Frame(self.pwd_border, bg=config.BG_INPUT)
        pwd_inner_frame.pack(fill=tk.X)

        self.entry_pwd = tk.Entry(
            pwd_inner_frame,
            bg=config.BG_INPUT,
            fg=config.COLOR_TEXT_PRIMARY,
            insertbackground=config.ACCENT_CYAN,
            relief=tk.FLAT,
            font=config.FONT_BODY,
            show="•"
        )
        self.entry_pwd.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=6)
        self.entry_pwd.insert(0, "admin123")
        self.entry_pwd.bind("<FocusIn>", lambda e: self.pwd_border.configure(bg=config.ACCENT_CYAN))
        self.entry_pwd.bind("<FocusOut>", lambda e: self.pwd_border.configure(bg=config.ACCENT_BORDER))
        self.entry_pwd.bind("<Return>", lambda e: self._attempt_login())

        # Show / Hide Password Eye Toggle
        self.btn_toggle_pwd = tk.Button(
            pwd_inner_frame,
            text="👁 SHOW",
            font=config.FONT_SMALL,
            bg=config.BG_INPUT,
            fg=config.ACCENT_CYAN,
            relief=tk.FLAT,
            cursor="hand2",
            bd=0,
            command=self._toggle_password_visibility
        )
        self.btn_toggle_pwd.pack(side=tk.RIGHT, padx=8)

        # Dynamic Error / Message Banner
        self.lbl_error = tk.Label(
            form_inner,
            text="",
            font=config.FONT_BODY_BOLD,
            fg=config.ACCENT_DANGER,
            bg=config.BG_CARD
        )
        self.lbl_error.pack(fill=tk.X, pady=(6, 8))

        # Futuristic Submit Button
        self.btn_login = GlowingButton(
            form_inner,
            text="⚡ INITIALIZE COMMAND ACCESS",
            theme="cyan",
            command=self._attempt_login
        )
        self.btn_login.pack(fill=tk.X, ipady=8, pady=(4, 8))

    def _apply_preset(self, username, password):
        self.entry_user.delete(0, tk.END)
        self.entry_user.insert(0, username)
        self.entry_pwd.delete(0, tk.END)
        self.entry_pwd.insert(0, password)
        self.lbl_error.configure(text=f"Preset loaded: {username}", fg=config.ACCENT_GREEN)

    def _toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.entry_pwd.configure(show="")
            self.btn_toggle_pwd.configure(text="🔒 HIDE")
        else:
            self.entry_pwd.configure(show="•")
            self.btn_toggle_pwd.configure(text="👁 SHOW")

    def _attempt_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pwd.get()

        if not username or not password:
            self.lbl_error.configure(text="Access Denied: Please enter both username and password.", fg=config.ACCENT_DANGER)
            return

        # Fetch user record from database
        user = db.get_user_by_username(username)
        if not user:
            self.lbl_error.configure(text="Access Denied: Operator identity not recognized.", fg=config.ACCENT_DANGER)
            return

        # Verify hashed password with salt
        is_valid = verify_password(password, user["password_hash"], user["salt"])
        if not is_valid:
            self.lbl_error.configure(text="Access Denied: Cryptographic key mismatch.", fg=config.ACCENT_DANGER)
            return

        # Successful Login
        self.lbl_error.configure(text="Clearance Confirmed. Granting Mainframe Access...", fg=config.ACCENT_GREEN)
        self.update_idletasks()

        # Update Session
        current_session.set_user(
            user_id=user["id"],
            username=user["username"],
            full_name=user["full_name"],
            role=user["role"],
            email=user.get("email", "")
        )

        # Log Activity
        db.log_activity(user["id"], "LOGIN_SUCCESS", f"User {user['username']} logged in as {user['role']}.")

        # Trigger voice welcome asynchronously
        voice_assistant.welcome_user(user["full_name"], user["role"])

        # Close login dialog and trigger callback
        self.after(350, self._finalize_success)

    def _finalize_success(self):
        self.destroy()
        self.on_success_callback()

    def _on_close(self):
        self.parent.destroy()
