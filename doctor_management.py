"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: doctor_management.py
Description: Specialist medical staff roster, departmental scheduling, consulting
             fee management, availability state toggles, and staff CRUD operations.
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import config
from database import db
from utils import GlowingButton, create_holographic_card, format_currency, validate_phone, validate_email, export_treeview_to_csv
from security import current_session


class DoctorManagementView(tk.Frame):
    """
    Physician Staff & Department Command Screen.
    """

    def __init__(self, parent, navigation_controller):
        super().__init__(parent, bg=config.BG_DARK)
        self.nav = navigation_controller

        self._build_ui()
        self.load_doctors()

    def _build_ui(self):
        self.main_container = tk.Frame(self, bg=config.BG_DARK)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # Header Control Bar
        header_card = create_holographic_card(self.main_container, title="PHYSICIAN ROSTER & SURGICAL DEPARTMENTS", subtitle="MEDICAL STAFF DIRECTORY")
        header_card.pack(fill=tk.X, pady=(0, 14))

        ctrl_frame = tk.Frame(header_card, bg=config.BG_CARD)
        ctrl_frame.pack(fill=tk.X, padx=14, pady=10)

        # Search Bar
        lbl_search = tk.Label(ctrl_frame, text="SEARCH STAFF:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_CYAN, bg=config.BG_CARD)
        lbl_search.pack(side=tk.LEFT, padx=(0, 6))

        search_border = tk.Frame(ctrl_frame, bg=config.ACCENT_BORDER, padx=1, pady=1)
        search_border.pack(side=tk.LEFT, padx=(0, 10))

        self.entry_search = tk.Entry(
            search_border,
            bg=config.BG_INPUT,
            fg=config.COLOR_TEXT_PRIMARY,
            insertbackground=config.ACCENT_CYAN,
            relief=tk.FLAT,
            font=config.FONT_BODY,
            width=20
        )
        self.entry_search.pack(ipady=5, padx=4)
        self.entry_search.bind("<KeyRelease>", lambda e: self.load_doctors())

        # Department / Specialization Filter Dropdown
        lbl_filter = tk.Label(ctrl_frame, text="SPECIALIZATION:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_CARD)
        lbl_filter.pack(side=tk.LEFT, padx=(6, 6))

        self.combo_filter = ttk.Combobox(
            ctrl_frame,
            values=["All Specializations"] + config.MEDICAL_SPECIALIZATIONS,
            state="readonly",
            width=24
        )
        self.combo_filter.set("All Specializations")
        self.combo_filter.pack(side=tk.LEFT, padx=(0, 12))
        self.combo_filter.bind("<<ComboboxSelected>>", lambda e: self.load_doctors())

        btn_search = GlowingButton(ctrl_frame, text="🔍 FILTER", theme="cyan", command=self.load_doctors)
        btn_search.pack(side=tk.LEFT, padx=(0, 12))

        # Action Buttons
        btn_add = GlowingButton(ctrl_frame, text="➕ ADD PHYSICIAN", theme="green", command=self._open_add_doctor_modal)
        btn_add.pack(side=tk.LEFT, padx=3)

        btn_edit = GlowingButton(ctrl_frame, text="✎ EDIT PROFILE", theme="blue", command=self._open_edit_doctor_modal)
        btn_edit.pack(side=tk.LEFT, padx=3)

        btn_status = GlowingButton(ctrl_frame, text="⚡ TOGGLE STATUS", theme="cyan", command=self._toggle_availability)
        btn_status.pack(side=tk.LEFT, padx=3)

        btn_delete = GlowingButton(ctrl_frame, text="✕ REMOVE", theme="danger", command=self._delete_doctor)
        btn_delete.pack(side=tk.LEFT, padx=3)

        btn_export = GlowingButton(ctrl_frame, text="⭳ EXPORT", theme="ghost", command=lambda: export_treeview_to_csv(self.tree, "doctors_roster.csv"))
        btn_export.pack(side=tk.RIGHT)

        # Table Container
        table_card = tk.Frame(self.main_container, bg=config.BG_CARD, highlightthickness=1, highlightbackground=config.ACCENT_BORDER)
        table_card.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "uid", "name", "specialization", "qualification", "phone", "room", "hours", "fee", "status")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("uid", text="DOCTOR UID")
        self.tree.heading("name", text="PHYSICIAN NAME")
        self.tree.heading("specialization", text="SPECIALIZATION")
        self.tree.heading("qualification", text="CREDENTIALS")
        self.tree.heading("phone", text="PHONE")
        self.tree.heading("room", text="SUITE / CLINIC")
        self.tree.heading("hours", text="VISITING SCHEDULE")
        self.tree.heading("fee", text="FEE (USD)")
        self.tree.heading("status", text="DUTY STATUS")

        self.tree.column("id", width=40, anchor=tk.CENTER)
        self.tree.column("uid", width=95, anchor=tk.CENTER)
        self.tree.column("name", width=180, anchor=tk.W)
        self.tree.column("specialization", width=190, anchor=tk.W)
        self.tree.column("qualification", width=160, anchor=tk.W)
        self.tree.column("phone", width=120, anchor=tk.CENTER)
        self.tree.column("room", width=140, anchor=tk.W)
        self.tree.column("hours", width=140, anchor=tk.CENTER)
        self.tree.column("fee", width=80, anchor=tk.E)
        self.tree.column("status", width=110, anchor=tk.CENTER)

        # Scrollbar
        scrollbar_y = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y, pady=8, padx=(0, 8))

        self.tree.bind("<Double-1>", lambda e: self._open_edit_doctor_modal())

    def load_doctors(self):
        """Query doctors table and refresh Treeview."""
        query = self.entry_search.get().strip()
        spec_filter = self.combo_filter.get()
        doctors = db.get_all_doctors(search_query=query, spec_filter=spec_filter)

        for row in self.tree.get_children():
            self.tree.delete(row)

        for d in doctors:
            self.tree.insert("", tk.END, values=(
                d["id"],
                d["doctor_uid"],
                d["full_name"],
                d["specialization"],
                d["qualification"],
                d["phone"],
                d["room_no"],
                d["visiting_hours"],
                format_currency(d["fee"]),
                d["status"]
            ))

    def _get_selected_doctor_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a physician from the roster.")
            return None
        return int(self.tree.item(selected[0])["values"][0])

    def _open_add_doctor_modal(self):
        DoctorFormModal(self, title="ENROLL NEW PHYSICIAN", mode="add", on_save_callback=self.load_doctors)

    def _open_edit_doctor_modal(self):
        doc_id = self._get_selected_doctor_id()
        if not doc_id:
            return
        doc = db.get_doctor_by_id(doc_id)
        if doc:
            DoctorFormModal(self, title="EDIT PHYSICIAN CREDENTIALS", mode="edit", doctor_data=doc, on_save_callback=self.load_doctors)

    def _toggle_availability(self):
        doc_id = self._get_selected_doctor_id()
        if not doc_id:
            return
        doc = db.get_doctor_by_id(doc_id)
        current_status = doc["status"]
        
        # Cycle through statuses: Available -> In Consultation -> In Surgery -> Off Duty -> Available
        cycle = {
            "Available": "In Consultation",
            "In Consultation": "In Surgery",
            "In Surgery": "Off Duty",
            "Off Duty": "Available"
        }
        new_status = cycle.get(current_status, "Available")
        
        doc_data = dict(doc)
        doc_data["status"] = new_status
        db.update_doctor(doc_id, doc_data)
        db.log_activity(current_session.user_id, "DOCTOR_STATUS_TOGGLE", f"Doctor {doc['full_name']} marked as {new_status}.")
        self.load_doctors()

    def _delete_doctor(self):
        doc_id = self._get_selected_doctor_id()
        if not doc_id:
            return
        doc = db.get_doctor_by_id(doc_id)
        confirm = messagebox.askyesno(
            "Confirm Staff Removal",
            f"Are you sure you want to remove physician profile:\n"
            f"[{doc['doctor_uid']}] {doc['full_name']}?\n\n"
            f"Warning: Linked appointments will be removed."
        )
        if confirm:
            db.delete_doctor(doc_id)
            db.log_activity(current_session.user_id, "DOCTOR_REMOVE", f"Removed doctor profile {doc['doctor_uid']}.")
            messagebox.showinfo("Staff Removed", "Doctor profile removed from active hospital records.")
            self.load_doctors()


class DoctorFormModal(tk.Toplevel):
    """
    Modal Dialog for creating and modifying doctor records.
    """

    def __init__(self, parent, title: str, mode: str = "add", doctor_data: dict = None, on_save_callback=None):
        super().__init__(parent)
        self.mode = mode
        self.doctor_data = doctor_data or {}
        self.on_save_callback = on_save_callback

        self.title(f"MEDNOVA AI — {title}")
        self.geometry("680x600")
        self.minsize(640, 560)
        self.configure(bg=config.BG_DARK)
        self.transient(parent)
        self.grab_set()

        self._center(680, 600)
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

        # Body
        body = tk.Frame(container, bg=config.BG_PANEL)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Row 1: Doctor UID & Name
        r1 = tk.Frame(body, bg=config.BG_PANEL)
        r1.pack(fill=tk.X, pady=6)

        self.uid_val = self.doctor_data.get("doctor_uid", db.get_next_doctor_uid())
        f_uid = tk.Frame(r1, bg=config.BG_PANEL)
        f_uid.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_uid, text="DOCTOR IDENTIFIER (UID):", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_uid = tk.Entry(f_uid, bg=config.BG_CARD, fg=config.ACCENT_CYAN, font=config.FONT_BODY_BOLD, relief=tk.FLAT)
        self.entry_uid.insert(0, self.uid_val)
        self.entry_uid.configure(state="readonly")
        self.entry_uid.pack(fill=tk.X, ipady=6, pady=(3, 0))

        f_name = tk.Frame(r1, bg=config.BG_PANEL)
        f_name.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_name, text="PHYSICIAN FULL NAME *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_name = tk.Entry(f_name, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_name.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_name.insert(0, self.doctor_data.get("full_name", ""))

        # Row 2: Specialization & Qualification
        r2 = tk.Frame(body, bg=config.BG_PANEL)
        r2.pack(fill=tk.X, pady=6)

        f_spec = tk.Frame(r2, bg=config.BG_PANEL)
        f_spec.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_spec, text="MEDICAL SPECIALIZATION *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.combo_spec = ttk.Combobox(f_spec, values=config.MEDICAL_SPECIALIZATIONS)
        self.combo_spec.set(self.doctor_data.get("specialization", config.MEDICAL_SPECIALIZATIONS[0]))
        self.combo_spec.pack(fill=tk.X, ipady=4, pady=(3, 0))

        f_qual = tk.Frame(r2, bg=config.BG_PANEL)
        f_qual.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_qual, text="QUALIFICATION & BOARD *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_qual = tk.Entry(f_qual, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_qual.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_qual.insert(0, self.doctor_data.get("qualification", "MD, FACS"))

        # Row 3: Phone & Email
        r3 = tk.Frame(body, bg=config.BG_PANEL)
        r3.pack(fill=tk.X, pady=6)

        f_ph = tk.Frame(r3, bg=config.BG_PANEL)
        f_ph.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_ph, text="OFFICE TELEPHONE *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_phone = tk.Entry(f_ph, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_phone.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_phone.insert(0, self.doctor_data.get("phone", "+1-800-555-"))

        f_em = tk.Frame(r3, bg=config.BG_PANEL)
        f_em.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_em, text="STAFF EMAIL:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_email = tk.Entry(f_em, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_email.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_email.insert(0, self.doctor_data.get("email", ""))

        # Row 4: Room No & Consultation Fee
        r4 = tk.Frame(body, bg=config.BG_PANEL)
        r4.pack(fill=tk.X, pady=6)

        f_rm = tk.Frame(r4, bg=config.BG_PANEL)
        f_rm.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_rm, text="CLINIC SUITE / ROOM NO *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_room = tk.Entry(f_rm, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_room.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_room.insert(0, self.doctor_data.get("room_no", "Suite 101"))

        f_fee = tk.Frame(r4, bg=config.BG_PANEL)
        f_fee.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_fee, text="CONSULTATION CHARGE ($) *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_fee = tk.Entry(f_fee, bg=config.BG_INPUT, fg=config.ACCENT_GREEN, font=config.FONT_BODY_BOLD, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_fee.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_fee.insert(0, str(self.doctor_data.get("fee", "200.00")))

        # Row 5: Visiting Hours & Status
        r5 = tk.Frame(body, bg=config.BG_PANEL)
        r5.pack(fill=tk.X, pady=6)

        f_hr = tk.Frame(r5, bg=config.BG_PANEL)
        f_hr.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_hr, text="VISITING CLINICAL HOURS *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_hours = tk.Entry(f_hr, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_hours.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_hours.insert(0, self.doctor_data.get("visiting_hours", "09:00 AM - 01:00 PM"))

        f_st = tk.Frame(r5, bg=config.BG_PANEL)
        f_st.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_st, text="DUTY STATUS *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.combo_status = ttk.Combobox(f_st, values=["Available", "In Consultation", "In Surgery", "Off Duty"], state="readonly")
        self.combo_status.set(self.doctor_data.get("status", "Available"))
        self.combo_status.pack(fill=tk.X, ipady=4, pady=(3, 0))

        # Footer Buttons
        btn_footer = tk.Frame(container, bg=config.BG_PANEL)
        btn_footer.pack(fill=tk.X, pady=(12, 16), padx=20)

        btn_save = GlowingButton(btn_footer, text="💾 COMMIT PHYSICIAN RECORD", theme="cyan", command=self._save_doctor)
        btn_save.pack(side=tk.RIGHT, padx=6)

        btn_cancel = GlowingButton(btn_footer, text="✕ CANCEL", theme="ghost", command=self.destroy)
        btn_cancel.pack(side=tk.RIGHT)

    def _save_doctor(self):
        name = self.entry_name.get().strip()
        spec = self.combo_spec.get().strip()
        qual = self.entry_qual.get().strip()
        phone = self.entry_phone.get().strip()
        email = self.entry_email.get().strip()
        room = self.entry_room.get().strip()
        fee_str = self.entry_fee.get().strip()
        hours = self.entry_hours.get().strip()
        status = self.combo_status.get().strip()

        if not name:
            messagebox.showerror("Validation Error", "Doctor Name is required.")
            return

        if not qual:
            messagebox.showerror("Validation Error", "Qualifications/Credentials are required.")
            return

        if not validate_phone(phone):
            messagebox.showerror("Validation Error", "Valid contact phone number is required.")
            return

        if email and not validate_email(email):
            messagebox.showerror("Validation Error", "Staff email format is invalid.")
            return

        try:
            fee = float(fee_str)
            if fee < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Consultation fee must be a positive number.")
            return

        doc_dict = {
            "doctor_uid": self.uid_val,
            "full_name": name,
            "specialization": spec,
            "qualification": qual,
            "phone": phone,
            "email": email,
            "room_no": room,
            "visiting_hours": hours,
            "fee": fee,
            "status": status
        }

        if self.mode == "add":
            db.insert_doctor(doc_dict)
            db.log_activity(current_session.user_id, "DOCTOR_ADD", f"Enrolled physician {name} ({self.uid_val}).")
            messagebox.showinfo("Physician Enrolled", f"{name} successfully registered into hospital roster.")
        else:
            db.update_doctor(self.doctor_data["id"], doc_dict)
            db.log_activity(current_session.user_id, "DOCTOR_UPDATE", f"Updated physician {name} ({self.uid_val}).")
            messagebox.showinfo("Update Confirmed", f"Credentials and schedule updated for {name}.")

        if self.on_save_callback:
            self.on_save_callback()

        self.destroy()
