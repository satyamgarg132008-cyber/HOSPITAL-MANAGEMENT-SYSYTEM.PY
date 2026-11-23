"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: patient_management.py
Description: Patient demographic registration, searchable patient registry,
             CRUD modal dialogs, input validation, and medical history link.
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from database import db
from utils import (
    GlowingButton, create_holographic_card, validate_phone,
    validate_email, calculate_age_from_dob, export_treeview_to_csv
)
from voice_engine import voice_assistant
from security import current_session


class PatientManagementView(tk.Frame):
    """
    Patient Registry Command Screen.
    """

    def __init__(self, parent, navigation_controller):
        super().__init__(parent, bg=config.BG_DARK)
        self.nav = navigation_controller

        self._build_ui()
        self.load_patients()

    def _build_ui(self):
        self.main_container = tk.Frame(self, bg=config.BG_DARK)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # Header Control Bar (Search, Filter, Action Buttons)
        header_card = create_holographic_card(self.main_container, title="PATIENT CENSUS COMMAND", subtitle="REGISTRY & BIOMETRICS")
        header_card.pack(fill=tk.X, pady=(0, 14))

        ctrl_frame = tk.Frame(header_card, bg=config.BG_CARD)
        ctrl_frame.pack(fill=tk.X, padx=14, pady=10)

        # Search Bar
        lbl_search = tk.Label(ctrl_frame, text="SEARCH REGISTRY:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_CYAN, bg=config.BG_CARD)
        lbl_search.pack(side=tk.LEFT, padx=(0, 8))

        search_border = tk.Frame(ctrl_frame, bg=config.ACCENT_BORDER, padx=1, pady=1)
        search_border.pack(side=tk.LEFT, padx=(0, 10))

        self.entry_search = tk.Entry(
            search_border,
            bg=config.BG_INPUT,
            fg=config.COLOR_TEXT_PRIMARY,
            insertbackground=config.ACCENT_CYAN,
            relief=tk.FLAT,
            font=config.FONT_BODY,
            width=28
        )
        self.entry_search.pack(ipady=5, padx=4)
        self.entry_search.bind("<KeyRelease>", lambda e: self.load_patients())

        btn_search = GlowingButton(ctrl_frame, text="🔍 QUERY", theme="cyan", command=self.load_patients)
        btn_search.pack(side=tk.LEFT, padx=(0, 16))

        # Action Buttons
        btn_add = GlowingButton(ctrl_frame, text="➕ NEW PATIENT", theme="green", command=self._open_add_patient_modal)
        btn_add.pack(side=tk.LEFT, padx=4)

        btn_edit = GlowingButton(ctrl_frame, text="✎ UPDATE RECORD", theme="blue", command=self._open_edit_patient_modal)
        btn_edit.pack(side=tk.LEFT, padx=4)

        btn_history = GlowingButton(ctrl_frame, text="📂 MEDICAL DOSSIER", theme="cyan", command=self._view_patient_dossier)
        btn_history.pack(side=tk.LEFT, padx=4)

        btn_delete = GlowingButton(ctrl_frame, text="✕ PURGE RECORD", theme="danger", command=self._delete_selected_patient)
        btn_delete.pack(side=tk.LEFT, padx=4)

        btn_export = GlowingButton(ctrl_frame, text="⭳ EXPORT CSV", theme="ghost", command=lambda: export_treeview_to_csv(self.tree, "patients_registry.csv"))
        btn_export.pack(side=tk.RIGHT, padx=4)

        # Table Container
        table_card = tk.Frame(self.main_container, bg=config.BG_CARD, highlightthickness=1, highlightbackground=config.ACCENT_BORDER)
        table_card.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "uid", "name", "dob", "age", "gender", "blood", "phone", "emergency", "reg_date", "status")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="DB ID")
        self.tree.heading("uid", text="PATIENT UID")
        self.tree.heading("name", text="FULL LEGAL NAME")
        self.tree.heading("dob", text="DOB")
        self.tree.heading("age", text="AGE")
        self.tree.heading("gender", text="GENDER")
        self.tree.heading("blood", text="BLOOD")
        self.tree.heading("phone", text="PHONE")
        self.tree.heading("emergency", text="EMERGENCY CONTACT")
        self.tree.heading("reg_date", text="REGISTRATION DATE")
        self.tree.heading("status", text="STATUS")

        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("uid", width=120, anchor=tk.CENTER)
        self.tree.column("name", width=180, anchor=tk.W)
        self.tree.column("dob", width=95, anchor=tk.CENTER)
        self.tree.column("age", width=50, anchor=tk.CENTER)
        self.tree.column("gender", width=75, anchor=tk.CENTER)
        self.tree.column("blood", width=65, anchor=tk.CENTER)
        self.tree.column("phone", width=120, anchor=tk.CENTER)
        self.tree.column("emergency", width=160, anchor=tk.W)
        self.tree.column("reg_date", width=140, anchor=tk.CENTER)
        self.tree.column("status", width=80, anchor=tk.CENTER)

        # Scrollbar
        scrollbar_y = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y, pady=8, padx=(0, 8))

        # Double click to edit
        self.tree.bind("<Double-1>", lambda e: self._open_edit_patient_modal())

    def load_patients(self):
        """Fetch matching patients from SQLite and populate the treeview."""
        query = self.entry_search.get().strip()
        patients = db.get_all_patients(search_query=query)

        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in patients:
            self.tree.insert("", tk.END, values=(
                p["id"],
                p["patient_uid"],
                p["full_name"],
                p["dob"],
                p["age"],
                p["gender"],
                p["blood_group"],
                p["phone"],
                p["emergency_contact"],
                p["registered_at"],
                p["status"]
            ))

    def _get_selected_patient_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a patient from the list.")
            return None
        item_vals = self.tree.item(selected[0])["values"]
        return int(item_vals[0])

    def _open_add_patient_modal(self):
        PatientFormModal(self, title="REGISTER NEW PATIENT", mode="add", on_save_callback=self.load_patients)

    def _open_edit_patient_modal(self):
        patient_id = self._get_selected_patient_id()
        if not patient_id:
            return
        patient = db.get_patient_by_id(patient_id)
        if patient:
            PatientFormModal(self, title="UPDATE PATIENT DOSSIER", mode="edit", patient_data=patient, on_save_callback=self.load_patients)

    def _delete_selected_patient(self):
        patient_id = self._get_selected_patient_id()
        if not patient_id:
            return
        patient = db.get_patient_by_id(patient_id)
        confirm = messagebox.askyesno(
            "Security Confirmation",
            f"Are you sure you want to permanently delete patient:\n"
            f"[{patient['patient_uid']}] {patient['full_name']}?\n\n"
            f"WARNING: All linked appointments, bills, and medical histories will be removed."
        )
        if confirm:
            db.delete_patient(patient_id)
            db.log_activity(current_session.user_id, "PATIENT_DELETE", f"Purged patient ID {patient['patient_uid']}.")
            messagebox.showinfo("Purge Confirmed", "Patient record and linked files successfully removed.")
            self.load_patients()

    def _view_patient_dossier(self):
        patient_id = self._get_selected_patient_id()
        if not patient_id:
            return
        # Navigate to medical history module focusing on this patient
        self.nav.navigate_to("medical_history", patient_id=patient_id)


class PatientFormModal(tk.Toplevel):
    """
    Futuristic Modal Dialog for adding or updating patient records.
    """

    def __init__(self, parent, title: str, mode: str = "add", patient_data: dict = None, on_save_callback=None):
        super().__init__(parent)
        self.mode = mode
        self.patient_data = patient_data or {}
        self.on_save_callback = on_save_callback

        self.title(f"MEDNOVA AI — {title}")
        self.geometry("680x620")
        self.minsize(640, 580)
        self.configure(bg=config.BG_DARK)
        self.transient(parent)
        self.grab_set()

        self._center(680, 620)
        self._build_ui(title)

    def _center(self, w, h):
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self, title_text):
        container = tk.Frame(self, bg=config.BG_PANEL, highlightthickness=2, highlightbackground=config.ACCENT_CYAN)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Header
        header = tk.Frame(container, bg=config.BG_DARK, height=50)
        header.pack(fill=tk.X)
        lbl_title = tk.Label(header, text=f"◈ {title_text}", font=config.FONT_SUBTITLE, fg=config.ACCENT_CYAN, bg=config.BG_DARK)
        lbl_title.pack(side=tk.LEFT, padx=16, pady=12)

        # Form Body
        body = tk.Frame(container, bg=config.BG_PANEL)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Row 1: Patient UID & Full Name
        r1 = tk.Frame(body, bg=config.BG_PANEL)
        r1.pack(fill=tk.X, pady=6)

        self.uid_val = self.patient_data.get("patient_uid", db.get_next_patient_uid())
        f_uid = tk.Frame(r1, bg=config.BG_PANEL)
        f_uid.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_uid, text="PATIENT IDENTIFIER (UID):", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_uid = tk.Entry(f_uid, bg=config.BG_CARD, fg=config.ACCENT_CYAN, font=config.FONT_BODY_BOLD, relief=tk.FLAT)
        self.entry_uid.insert(0, self.uid_val)
        self.entry_uid.configure(state="readonly")
        self.entry_uid.pack(fill=tk.X, ipady=6, pady=(3, 0))

        f_name = tk.Frame(r1, bg=config.BG_PANEL)
        f_name.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_name, text="FULL LEGAL NAME *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_name = tk.Entry(f_name, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_name.pack(fill=tk.X, ipady=6, pady=(3, 0))
        if self.patient_data:
            self.entry_name.insert(0, self.patient_data.get("full_name", ""))

        # Row 2: DOB & Age
        r2 = tk.Frame(body, bg=config.BG_PANEL)
        r2.pack(fill=tk.X, pady=6)

        f_dob = tk.Frame(r2, bg=config.BG_PANEL)
        f_dob.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_dob, text="DATE OF BIRTH (YYYY-MM-DD) *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_dob = tk.Entry(f_dob, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_dob.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_dob.insert(0, self.patient_data.get("dob", "2000-01-01"))
        self.entry_dob.bind("<KeyRelease>", self._auto_calculate_age)

        f_age = tk.Frame(r2, bg=config.BG_PANEL)
        f_age.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_age, text="AGE (YEARS):", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_age = tk.Entry(f_age, bg=config.BG_INPUT, fg=config.ACCENT_GREEN, font=config.FONT_BODY_BOLD, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_age.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_age.insert(0, str(self.patient_data.get("age", "26")))

        # Row 3: Gender & Blood Group
        r3 = tk.Frame(body, bg=config.BG_PANEL)
        r3.pack(fill=tk.X, pady=6)

        f_gen = tk.Frame(r3, bg=config.BG_PANEL)
        f_gen.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_gen, text="GENDER *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.combo_gender = ttk.Combobox(f_gen, values=["Male", "Female", "Other", "Undisclosed"], state="readonly")
        self.combo_gender.set(self.patient_data.get("gender", "Male"))
        self.combo_gender.pack(fill=tk.X, ipady=4, pady=(3, 0))

        f_bld = tk.Frame(r3, bg=config.BG_PANEL)
        f_bld.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_bld, text="BLOOD GROUP *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.combo_blood = ttk.Combobox(f_bld, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], state="readonly")
        self.combo_blood.set(self.patient_data.get("blood_group", "O+"))
        self.combo_blood.pack(fill=tk.X, ipady=4, pady=(3, 0))

        # Row 4: Phone & Email
        r4 = tk.Frame(body, bg=config.BG_PANEL)
        r4.pack(fill=tk.X, pady=6)

        f_ph = tk.Frame(r4, bg=config.BG_PANEL)
        f_ph.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_ph, text="CONTACT TELEPHONE *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_phone = tk.Entry(f_ph, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_phone.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_phone.insert(0, self.patient_data.get("phone", ""))

        f_em = tk.Frame(r4, bg=config.BG_PANEL)
        f_em.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_em, text="EMAIL ADDRESS:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_email = tk.Entry(f_em, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_email.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_email.insert(0, self.patient_data.get("email", ""))

        # Row 5: Emergency Contact
        r5 = tk.Frame(body, bg=config.BG_PANEL)
        r5.pack(fill=tk.X, pady=6)
        tk.Label(r5, text="EMERGENCY CONTACT (NAME & RELATION / PHONE) *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_emergency = tk.Entry(r5, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_emergency.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_emergency.insert(0, self.patient_data.get("emergency_contact", ""))

        # Row 6: Address
        r6 = tk.Frame(body, bg=config.BG_PANEL)
        r6.pack(fill=tk.X, pady=6)
        tk.Label(r6, text="RESIDENTIAL LOCATION / ADDRESS:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_addr = tk.Entry(r6, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_addr.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_addr.insert(0, self.patient_data.get("address", ""))

        # Footer Buttons
        btn_footer = tk.Frame(container, bg=config.BG_PANEL)
        btn_footer.pack(fill=tk.X, pady=(12, 16), padx=20)

        btn_save = GlowingButton(btn_footer, text="💾 COMMIT TO DATABASE", theme="cyan", command=self._save_patient)
        btn_save.pack(side=tk.RIGHT, padx=6)

        btn_cancel = GlowingButton(btn_footer, text="✕ CANCEL", theme="ghost", command=self.destroy)
        btn_cancel.pack(side=tk.RIGHT)

    def _auto_calculate_age(self, event=None):
        dob_text = self.entry_dob.get().strip()
        calculated_age = calculate_age_from_dob(dob_text)
        if calculated_age > 0:
            self.entry_age.delete(0, tk.END)
            self.entry_age.insert(0, str(calculated_age))

    def _save_patient(self):
        full_name = self.entry_name.get().strip()
        dob = self.entry_dob.get().strip()
        age_str = self.entry_age.get().strip()
        gender = self.combo_gender.get().strip()
        blood = self.combo_blood.get().strip()
        phone = self.entry_phone.get().strip()
        email = self.entry_email.get().strip()
        emergency = self.entry_emergency.get().strip()
        address = self.entry_addr.get().strip()

        # Validation
        if not full_name:
            messagebox.showerror("Validation Error", "Full Name is required.")
            return

        if not dob or len(dob) != 10:
            messagebox.showerror("Validation Error", "DOB must be in YYYY-MM-DD format.")
            return

        try:
            age = int(age_str)
            if age < 0 or age > 130:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Age must be a valid positive integer.")
            return

        if not validate_phone(phone):
            messagebox.showerror("Validation Error", "Please provide a valid phone number with at least 7 digits.")
            return

        if email and not validate_email(email):
            messagebox.showerror("Validation Error", "Email address format is invalid.")
            return

        if not emergency:
            messagebox.showerror("Validation Error", "Emergency contact is mandatory for patient intake safety.")
            return

        patient_dict = {
            "patient_uid": self.uid_val,
            "full_name": full_name,
            "dob": dob,
            "age": age,
            "gender": gender,
            "blood_group": blood,
            "phone": phone,
            "email": email,
            "address": address,
            "emergency_contact": emergency,
            "registered_at": self.patient_data.get("registered_at", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "status": "Active"
        }

        if self.mode == "add":
            new_id = db.insert_patient(patient_dict)
            db.log_activity(current_session.user_id, "PATIENT_REGISTER", f"Registered {full_name} ({self.uid_val}).")
            voice_assistant.announce_patient_registered(full_name, self.uid_val)
            messagebox.showinfo("Registry Success", f"Patient {full_name} successfully enrolled with UID {self.uid_val}.")
        else:
            db.update_patient(self.patient_data["id"], patient_dict)
            db.log_activity(current_session.user_id, "PATIENT_UPDATE", f"Updated dossier for {full_name} ({self.uid_val}).")
            messagebox.showinfo("Update Success", f"Patient dossier for {full_name} updated successfully.")

        if self.on_save_callback:
            self.on_save_callback()

        self.destroy()
