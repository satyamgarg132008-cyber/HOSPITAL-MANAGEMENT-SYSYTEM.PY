"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: appointment_management.py
Description: Clinical appointment booking engine, real-time schedule conflict
             resolution, multi-status lifecycle tracking, and calendar synchronization.
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from database import db
from utils import GlowingButton, create_holographic_card, export_treeview_to_csv
from voice_engine import voice_assistant
from security import current_session


class AppointmentManagementView(tk.Frame):
    """
    Appointments & Surgical Scheduling Screen.
    """

    def __init__(self, parent, navigation_controller):
        super().__init__(parent, bg=config.BG_DARK)
        self.nav = navigation_controller

        self._build_ui()
        self.load_appointments()

    def _build_ui(self):
        self.main_container = tk.Frame(self, bg=config.BG_DARK)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # Header Control Bar
        header_card = create_holographic_card(self.main_container, title="CLINICAL APPOINTMENTS & SURGERY SCHEDULER", subtitle="AI CONFLICT RESOLUTION MATRIX")
        header_card.pack(fill=tk.X, pady=(0, 14))

        ctrl_frame = tk.Frame(header_card, bg=config.BG_CARD)
        ctrl_frame.pack(fill=tk.X, padx=14, pady=10)

        # Search Bar
        lbl_search = tk.Label(ctrl_frame, text="QUERY APPOINTMENTS:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_CYAN, bg=config.BG_CARD)
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
            width=18
        )
        self.entry_search.pack(ipady=5, padx=4)
        self.entry_search.bind("<KeyRelease>", lambda e: self.load_appointments())

        # Status Filter
        lbl_st = tk.Label(ctrl_frame, text="STATUS:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_CARD)
        lbl_st.pack(side=tk.LEFT, padx=(4, 6))

        self.combo_status = ttk.Combobox(
            ctrl_frame,
            values=["All Statuses", "Scheduled", "Completed", "In Progress", "Cancelled"],
            state="readonly",
            width=14
        )
        self.combo_status.set("All Statuses")
        self.combo_status.pack(side=tk.LEFT, padx=(0, 10))
        self.combo_status.bind("<<ComboboxSelected>>", lambda e: self.load_appointments())

        # Quick Date Filter
        btn_today = GlowingButton(ctrl_frame, text="TODAY", theme="ghost", command=self._filter_today)
        btn_today.pack(side=tk.LEFT, padx=2)

        btn_all = GlowingButton(ctrl_frame, text="ALL", theme="ghost", command=self._clear_date_filter)
        btn_all.pack(side=tk.LEFT, padx=(2, 10))

        # Main Action Buttons
        btn_book = GlowingButton(ctrl_frame, text="➕ BOOK VISIT", theme="green", command=self._open_book_modal)
        btn_book.pack(side=tk.LEFT, padx=3)

        btn_resched = GlowingButton(ctrl_frame, text="📅 RESCHEDULE", theme="blue", command=self._open_reschedule_modal)
        btn_resched.pack(side=tk.LEFT, padx=3)

        btn_complete = GlowingButton(ctrl_frame, text="✓ COMPLETE", theme="cyan", command=self._mark_completed)
        btn_complete.pack(side=tk.LEFT, padx=3)

        btn_cancel = GlowingButton(ctrl_frame, text="✕ CANCEL", theme="danger", command=self._cancel_appointment)
        btn_cancel.pack(side=tk.LEFT, padx=3)

        btn_export = GlowingButton(ctrl_frame, text="⭳ EXPORT", theme="ghost", command=lambda: export_treeview_to_csv(self.tree, "appointments_schedule.csv"))
        btn_export.pack(side=tk.RIGHT)

        # Appointments Treeview Table
        table_card = tk.Frame(self.main_container, bg=config.BG_CARD, highlightthickness=1, highlightbackground=config.ACCENT_BORDER)
        table_card.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "uid", "date", "time", "patient", "doctor", "specialization", "room", "reason", "status")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("uid", text="APT UID")
        self.tree.heading("date", text="DATE")
        self.tree.heading("time", text="TIME SLOT")
        self.tree.heading("patient", text="PATIENT")
        self.tree.heading("doctor", text="ATTENDING PHYSICIAN")
        self.tree.heading("specialization", text="SPECIALIZATION")
        self.tree.heading("room", text="SUITE")
        self.tree.heading("reason", text="CLINICAL REASON")
        self.tree.heading("status", text="STATUS")

        self.tree.column("id", width=40, anchor=tk.CENTER)
        self.tree.column("uid", width=105, anchor=tk.CENTER)
        self.tree.column("date", width=95, anchor=tk.CENTER)
        self.tree.column("time", width=85, anchor=tk.CENTER)
        self.tree.column("patient", width=150, anchor=tk.W)
        self.tree.column("doctor", width=170, anchor=tk.W)
        self.tree.column("specialization", width=180, anchor=tk.W)
        self.tree.column("room", width=120, anchor=tk.W)
        self.tree.column("reason", width=180, anchor=tk.W)
        self.tree.column("status", width=95, anchor=tk.CENTER)

        # Scrollbar
        scrollbar_y = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y, pady=8, padx=(0, 8))

        self.active_date_filter = ""

    def load_appointments(self):
        """Fetch filtered appointments from SQLite and display in Treeview."""
        query = self.entry_search.get().strip()
        status_filter = self.combo_status.get()
        apts = db.get_all_appointments(
            status_filter=status_filter,
            date_filter=self.active_date_filter,
            search_query=query
        )

        for row in self.tree.get_children():
            self.tree.delete(row)

        for a in apts:
            self.tree.insert("", tk.END, values=(
                a["id"],
                a["appointment_uid"],
                a["appointment_date"],
                a["appointment_time"],
                a["patient_name"],
                a["doctor_name"],
                a["specialization"],
                a["room_no"],
                a["reason"],
                a["status"]
            ))

    def _filter_today(self):
        self.active_date_filter = datetime.date.today().strftime("%Y-%m-%d")
        self.load_appointments()

    def _clear_date_filter(self):
        self.active_date_filter = ""
        self.load_appointments()

    def _get_selected_appointment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an appointment from the table.")
            return None
        item_vals = self.tree.item(selected[0])["values"]
        apt_id = int(item_vals[0])
        # Find raw appointment dict
        for a in db.get_all_appointments():
            if a["id"] == apt_id:
                return a
        return None

    def _open_book_modal(self):
        BookAppointmentModal(self, on_save_callback=self.load_appointments)

    def _open_reschedule_modal(self):
        apt = self._get_selected_appointment()
        if not apt:
            return
        RescheduleModal(self, appointment_data=apt, on_save_callback=self.load_appointments)

    def _mark_completed(self):
        apt = self._get_selected_appointment()
        if not apt:
            return
        db.update_appointment_status(apt["id"], "Completed")
        db.log_activity(current_session.user_id, "APPOINTMENT_COMPLETE", f"Appointment {apt['appointment_uid']} marked as Completed.")
        messagebox.showinfo("Status Updated", f"Appointment {apt['appointment_uid']} for {apt['patient_name']} marked as COMPLETED.")
        self.load_appointments()

    def _cancel_appointment(self):
        apt = self._get_selected_appointment()
        if not apt:
            return
        confirm = messagebox.askyesno(
            "Confirm Cancellation",
            f"Are you sure you want to cancel appointment:\n"
            f"[{apt['appointment_uid']}] {apt['patient_name']} with {apt['doctor_name']}?"
        )
        if confirm:
            db.update_appointment_status(apt["id"], "Cancelled")
            db.log_activity(current_session.user_id, "APPOINTMENT_CANCEL", f"Cancelled appointment {apt['appointment_uid']}.")
            messagebox.showinfo("Appointment Cancelled", "The appointment status was changed to CANCELLED.")
            self.load_appointments()


class BookAppointmentModal(tk.Toplevel):
    """
    Modal Dialog with intelligent conflict detection for scheduling visits.
    """

    def __init__(self, parent, on_save_callback=None):
        super().__init__(parent)
        self.on_save_callback = on_save_callback

        self.title("MEDNOVA AI — CLINICAL APPOINTMENT DISPATCH")
        self.geometry("680x620")
        self.minsize(640, 580)
        self.configure(bg=config.BG_DARK)
        self.transient(parent)
        self.grab_set()

        self._center(680, 620)
        self.patients_list = db.get_all_patients()
        self.doctors_list = db.get_all_doctors()

        self._build_ui()

    def _center(self, w, h):
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        container = tk.Frame(self, bg=config.BG_PANEL, highlightthickness=2, highlightbackground=config.ACCENT_CYAN)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Header
        header = tk.Frame(container, bg=config.BG_DARK, height=50)
        header.pack(fill=tk.X)
        lbl_title = tk.Label(header, text="◈ SCHEDULE CLINICAL CONSULTATION", font=config.FONT_SUBTITLE, fg=config.ACCENT_CYAN, bg=config.BG_DARK)
        lbl_title.pack(side=tk.LEFT, padx=16, pady=12)

        # Body
        body = tk.Frame(container, bg=config.BG_PANEL)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Row 1: Patient Selection Dropdown
        r1 = tk.Frame(body, bg=config.BG_PANEL)
        r1.pack(fill=tk.X, pady=6)
        tk.Label(r1, text="SELECT REGISTERED PATIENT *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)

        patient_options = [f"{p['patient_uid']} — {p['full_name']} (Phone: {p['phone']})" for p in self.patients_list]
        self.combo_patient = ttk.Combobox(r1, values=patient_options, state="readonly")
        if patient_options:
            self.combo_patient.set(patient_options[0])
        self.combo_patient.pack(fill=tk.X, ipady=4, pady=(3, 0))

        # Row 2: Doctor Selection Dropdown
        r2 = tk.Frame(body, bg=config.BG_PANEL)
        r2.pack(fill=tk.X, pady=6)
        tk.Label(r2, text="SELECT ATTENDING PHYSICIAN *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)

        doctor_options = [f"{d['doctor_uid']} — {d['full_name']} [{d['specialization']}] (Fee: ${d['fee']:.2f})" for d in self.doctors_list]
        self.combo_doctor = ttk.Combobox(r2, values=doctor_options, state="readonly")
        if doctor_options:
            self.combo_doctor.set(doctor_options[0])
        self.combo_doctor.pack(fill=tk.X, ipady=4, pady=(3, 0))

        # Row 3: Appointment Date & Time Slot
        r3 = tk.Frame(body, bg=config.BG_PANEL)
        r3.pack(fill=tk.X, pady=6)

        f_date = tk.Frame(r3, bg=config.BG_PANEL)
        f_date.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_date, text="APPOINTMENT DATE (YYYY-MM-DD) *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_date = tk.Entry(f_date, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_date.pack(fill=tk.X, ipady=6, pady=(3, 0))
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        self.entry_date.insert(0, today_str)

        f_time = tk.Frame(r3, bg=config.BG_PANEL)
        f_time.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_time, text="CONSULTATION TIME SLOT *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.combo_time = ttk.Combobox(f_time, values=config.APPOINTMENT_TIME_SLOTS, state="readonly")
        self.combo_time.set(config.APPOINTMENT_TIME_SLOTS[0])
        self.combo_time.pack(fill=tk.X, ipady=4, pady=(3, 0))

        # Quick Date Buttons (Today, Tomorrow, +2 Days)
        r_btns = tk.Frame(body, bg=config.BG_PANEL)
        r_btns.pack(fill=tk.X, pady=(2, 8))

        def set_date_offset(days):
            target = (datetime.date.today() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
            self.entry_date.delete(0, tk.END)
            self.entry_date.insert(0, target)

        tk.Button(r_btns, text="Today", font=config.FONT_SMALL, bg="#0D223A", fg=config.ACCENT_CYAN, relief=tk.FLAT, command=lambda: set_date_offset(0)).pack(side=tk.LEFT, padx=2)
        tk.Button(r_btns, text="Tomorrow", font=config.FONT_SMALL, bg="#0D223A", fg=config.ACCENT_CYAN, relief=tk.FLAT, command=lambda: set_date_offset(1)).pack(side=tk.LEFT, padx=2)
        tk.Button(r_btns, text="+2 Days", font=config.FONT_SMALL, bg="#0D223A", fg=config.ACCENT_CYAN, relief=tk.FLAT, command=lambda: set_date_offset(2)).pack(side=tk.LEFT, padx=2)

        # Row 4: Reason for Visit
        r4 = tk.Frame(body, bg=config.BG_PANEL)
        r4.pack(fill=tk.X, pady=6)
        tk.Label(r4, text="CHIEF COMPLAINT / CLINICAL REASON *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_reason = tk.Entry(r4, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_reason.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_reason.insert(0, "Routine specialist consultation & vitals examination")

        # Row 5: Preparation Notes
        r5 = tk.Frame(body, bg=config.BG_PANEL)
        r5.pack(fill=tk.X, pady=6)
        tk.Label(r5, text="PRE-CONSULTATION INSTRUCTIONS / NOTES:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_notes = tk.Entry(r5, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_notes.pack(fill=tk.X, ipady=6, pady=(3, 0))

        # Footer Buttons
        btn_footer = tk.Frame(container, bg=config.BG_PANEL)
        btn_footer.pack(fill=tk.X, pady=(16, 16), padx=20)

        btn_commit = GlowingButton(btn_footer, text="⚡ CONFIRM & DISPATCH BOOKING", theme="cyan", command=self._confirm_booking)
        btn_commit.pack(side=tk.RIGHT, padx=6)

        btn_cancel = GlowingButton(btn_footer, text="✕ CANCEL", theme="ghost", command=self.destroy)
        btn_cancel.pack(side=tk.RIGHT)

    def _confirm_booking(self):
        pat_idx = self.combo_patient.current()
        doc_idx = self.combo_doctor.current()
        apt_date = self.entry_date.get().strip()
        apt_time = self.combo_time.get().strip()
        reason = self.entry_reason.get().strip()
        notes = self.entry_notes.get().strip()

        if pat_idx < 0 or doc_idx < 0:
            messagebox.showerror("Error", "Please select both a patient and a doctor.")
            return

        if not apt_date or len(apt_date) != 10:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
            return

        if not reason:
            messagebox.showerror("Error", "Clinical reason cannot be empty.")
            return

        patient = self.patients_list[pat_idx]
        doctor = self.doctors_list[doc_idx]

        # Intelligent Conflict Detection!
        has_conflict = db.check_appointment_conflict(
            doctor_id=doctor["id"],
            appointment_date=apt_date,
            appointment_time=apt_time
        )
        if has_conflict:
            messagebox.showerror(
                "Booking Conflict Detected",
                f"SCHEDULE COLLISION:\n\n"
                f"{doctor['full_name']} is ALREADY BOOKED for a consultation on {apt_date} at {apt_time}.\n\n"
                f"Please choose an alternate time slot or select another specialist."
            )
            return

        apt_uid = db.get_next_appointment_uid()
        apt_dict = {
            "appointment_uid": apt_uid,
            "patient_id": patient["id"],
            "doctor_id": doctor["id"],
            "appointment_date": apt_date,
            "appointment_time": apt_time,
            "reason": reason,
            "status": "Scheduled",
            "notes": notes,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        db.insert_appointment(apt_dict)
        db.log_activity(
            current_session.user_id,
            "APPOINTMENT_BOOK",
            f"Booked {apt_uid} for {patient['full_name']} with {doctor['full_name']} on {apt_date} at {apt_time}."
        )

        voice_assistant.announce_appointment_booked(patient["full_name"], doctor["full_name"], apt_date)
        messagebox.showinfo(
            "Booking Confirmed",
            f"APPOINTMENT CONFIRMED!\n\n"
            f"ID: {apt_uid}\n"
            f"Patient: {patient['full_name']}\n"
            f"Physician: {doctor['full_name']}\n"
            f"Schedule: {apt_date} at {apt_time}\n"
            f"Clinic Suite: {doctor['room_no']}"
        )

        if self.on_save_callback:
            self.on_save_callback()

        self.destroy()


class RescheduleModal(tk.Toplevel):
    """
    Modal to reschedule appointment date and time slot.
    """

    def __init__(self, parent, appointment_data: dict, on_save_callback=None):
        super().__init__(parent)
        self.apt = appointment_data
        self.on_save_callback = on_save_callback

        self.title("MEDNOVA AI — RESCHEDULE CONSULTATION")
        self.geometry("540x420")
        self.configure(bg=config.BG_DARK)
        self.transient(parent)
        self.grab_set()

        self._center(540, 420)
        self._build_ui()

    def _center(self, w, h):
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        container = tk.Frame(self, bg=config.BG_PANEL, highlightthickness=2, highlightbackground=config.ACCENT_CYAN)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        header = tk.Label(
            container,
            text=f"◈ RESCHEDULE: {self.apt['appointment_uid']}",
            font=config.FONT_SUBTITLE,
            fg=config.ACCENT_CYAN,
            bg=config.BG_PANEL
        )
        header.pack(anchor=tk.W, padx=16, pady=(16, 10))

        info_lbl = tk.Label(
            container,
            text=f"Patient: {self.apt['patient_name']}\nPhysician: {self.apt['doctor_name']}\nCurrent: {self.apt['appointment_date']} at {self.apt['appointment_time']}",
            font=config.FONT_BODY,
            fg=config.COLOR_TEXT_SECONDARY,
            bg=config.BG_PANEL,
            justify=tk.LEFT
        )
        info_lbl.pack(anchor=tk.W, padx=16, pady=(0, 14))

        # New Date
        f_date = tk.Frame(container, bg=config.BG_PANEL)
        f_date.pack(fill=tk.X, padx=16, pady=6)
        tk.Label(f_date, text="NEW APPOINTMENT DATE (YYYY-MM-DD):", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_new_date = tk.Entry(f_date, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_new_date.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_new_date.insert(0, self.apt["appointment_date"])

        # New Time
        f_time = tk.Frame(container, bg=config.BG_PANEL)
        f_time.pack(fill=tk.X, padx=16, pady=6)
        tk.Label(f_time, text="NEW TIME SLOT:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.combo_new_time = ttk.Combobox(f_time, values=config.APPOINTMENT_TIME_SLOTS, state="readonly")
        self.combo_new_time.set(self.apt["appointment_time"])
        self.combo_new_time.pack(fill=tk.X, ipady=4, pady=(3, 0))

        # Footer
        btn_footer = tk.Frame(container, bg=config.BG_PANEL)
        btn_footer.pack(fill=tk.X, pady=(24, 16), padx=16)

        btn_save = GlowingButton(btn_footer, text="UPDATE SCHEDULE", theme="cyan", command=self._save_reschedule)
        btn_save.pack(side=tk.RIGHT, padx=6)

        btn_cancel = GlowingButton(btn_footer, text="CANCEL", theme="ghost", command=self.destroy)
        btn_cancel.pack(side=tk.RIGHT)

    def _save_reschedule(self):
        new_date = self.entry_new_date.get().strip()
        new_time = self.combo_new_time.get().strip()

        if not new_date or len(new_date) != 10:
            messagebox.showerror("Error", "Date must be YYYY-MM-DD.")
            return

        # Conflict check excluding this appointment
        has_conflict = db.check_appointment_conflict(
            doctor_id=self.apt["doctor_id"],
            appointment_date=new_date,
            appointment_time=new_time,
            exclude_id=self.apt["id"]
        )
        if has_conflict:
            messagebox.showerror("Conflict", f"Physician is already scheduled on {new_date} at {new_time}.")
            return

        db.reschedule_appointment(self.apt["id"], new_date, new_time, "[Rescheduled by operator]")
        db.log_activity(current_session.user_id, "APPOINTMENT_RESCHEDULE", f"Rescheduled {self.apt['appointment_uid']} to {new_date} {new_time}.")
        messagebox.showinfo("Rescheduled", f"Appointment successfully updated to {new_date} at {new_time}.")

        if self.on_save_callback:
            self.on_save_callback()

        self.destroy()
