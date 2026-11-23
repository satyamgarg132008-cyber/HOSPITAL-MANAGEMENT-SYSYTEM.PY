"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: medical_history.py
Description: Administrative electronic health records (EHR) & chronological clinical
             dossier viewer. Supports clinical note logging, prescription tracking,
             and physician attribution.
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from database import db
from utils import GlowingButton, create_holographic_card, export_treeview_to_csv
from security import current_session


class MedicalHistoryView(tk.Frame):
    """
    Electronic Health Records (EHR) & Clinical Dossier Screen.
    """

    def __init__(self, parent, navigation_controller, initial_patient_id=None):
        super().__init__(parent, bg=config.BG_DARK)
        self.nav = navigation_controller
        self.selected_patient_id = initial_patient_id

        self._build_ui()
        self.load_patients_dropdown()

    def _build_ui(self):
        self.main_container = tk.Frame(self, bg=config.BG_DARK)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # Header Control Bar
        header_card = create_holographic_card(self.main_container, title="CLINICAL ARCHIVE & PATIENT MEDICAL DOSSIER", subtitle="ADMINISTRATIVE EHR")
        header_card.pack(fill=tk.X, pady=(0, 14))

        ctrl_frame = tk.Frame(header_card, bg=config.BG_CARD)
        ctrl_frame.pack(fill=tk.X, padx=14, pady=10)

        # Patient Selector Dropdown
        lbl_pat = tk.Label(ctrl_frame, text="SELECT PATIENT DOSSIER:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_CYAN, bg=config.BG_CARD)
        lbl_pat.pack(side=tk.LEFT, padx=(0, 8))

        self.combo_patient = ttk.Combobox(ctrl_frame, state="readonly", width=38)
        self.combo_patient.pack(side=tk.LEFT, padx=(0, 12))
        self.combo_patient.bind("<<ComboboxSelected>>", self._on_patient_selected)

        btn_new_entry = GlowingButton(ctrl_frame, text="➕ ADD CLINICAL ENCOUNTER", theme="green", command=self._open_add_encounter_modal)
        btn_new_entry.pack(side=tk.LEFT, padx=4)

        btn_export = GlowingButton(ctrl_frame, text="⭳ EXPORT HISTORY", theme="ghost", command=lambda: export_treeview_to_csv(self.tree_history, "medical_history_dossier.csv"))
        btn_export.pack(side=tk.RIGHT)

        # Top Patient Demographics Banner Card
        self.demo_card = create_holographic_card(self.main_container, title="BIOMETRIC & DEMOGRAPHIC SUMMARY", subtitle="ACTIVE PATIENT")
        self.demo_card.pack(fill=tk.X, pady=(0, 12))

        self.lbl_demographics = tk.Label(
            self.demo_card,
            text="No patient selected. Please select a patient record from the selector above.",
            font=config.FONT_BODY,
            fg=config.COLOR_TEXT_SECONDARY,
            bg=config.BG_CARD,
            padx=14,
            pady=8
        )
        self.lbl_demographics.pack(anchor=tk.W)

        # Split Container: Chronological Encounters Table (Top) & Selected Encounter Detailed Note View (Bottom)
        split_frame = tk.Frame(self.main_container, bg=config.BG_DARK)
        split_frame.pack(fill=tk.BOTH, expand=True)

        # Encounters Table
        table_card = tk.Frame(split_frame, bg=config.BG_CARD, highlightthickness=1, highlightbackground=config.ACCENT_BORDER)
        table_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ("id", "date", "doctor", "specialization", "diagnosis", "treatment", "prescriptions")
        self.tree_history = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse", height=5)

        self.tree_history.heading("id", text="ID")
        self.tree_history.heading("date", text="VISIT DATE")
        self.tree_history.heading("doctor", text="ATTENDING PHYSICIAN")
        self.tree_history.heading("specialization", text="SPECIALIZATION")
        self.tree_history.heading("diagnosis", text="CLINICAL DIAGNOSIS NOTES")
        self.tree_history.heading("treatment", text="TREATMENT / PROCEDURES")
        self.tree_history.heading("prescriptions", text="PRESCRIBED MEDICATIONS")

        self.tree_history.column("id", width=40, anchor=tk.CENTER)
        self.tree_history.column("date", width=95, anchor=tk.CENTER)
        self.tree_history.column("doctor", width=170, anchor=tk.W)
        self.tree_history.column("specialization", width=180, anchor=tk.W)
        self.tree_history.column("diagnosis", width=220, anchor=tk.W)
        self.tree_history.column("treatment", width=220, anchor=tk.W)
        self.tree_history.column("prescriptions", width=200, anchor=tk.W)

        scrollbar_y = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree_history.yview)
        self.tree_history.configure(yscrollcommand=scrollbar_y.set)

        self.tree_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y, pady=8, padx=(0, 8))

        self.tree_history.bind("<<TreeviewSelect>>", self._on_encounter_selected)

        # Bottom Detail Preview Card
        detail_card = create_holographic_card(split_frame, title="CLINICAL ENCOUNTER DETAIL DOSSIER", subtitle="ADMINISTRATIVE DEMO DATA")
        detail_card.pack(fill=tk.BOTH, expand=True)

        self.txt_detail = tk.Text(
            detail_card,
            bg=config.BG_INPUT,
            fg=config.COLOR_TEXT_PRIMARY,
            font=config.FONT_MONO,
            relief=tk.FLAT,
            height=6,
            padx=12,
            pady=8
        )
        self.txt_detail.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 10))
        self.txt_detail.insert(tk.END, "Select an encounter record from the table above to view full clinical notes.\n\nDISCLAIMER: Records are for university demonstration only.")
        self.txt_detail.configure(state="disabled")

    def load_patients_dropdown(self):
        """Populate patient combobox and select either initial ID or first patient."""
        self.patients = db.get_all_patients()
        options = [f"{p['patient_uid']} — {p['full_name']} (DOB: {p['dob']})" for p in self.patients]
        self.combo_patient["values"] = options

        if not options:
            return

        selected_idx = 0
        if self.selected_patient_id:
            for idx, p in enumerate(self.patients):
                if p["id"] == self.selected_patient_id:
                    selected_idx = idx
                    break

        self.combo_patient.current(selected_idx)
        self._on_patient_selected()

    def _on_patient_selected(self, event=None):
        idx = self.combo_patient.current()
        if idx < 0:
            return

        patient = self.patients[idx]
        self.selected_patient_id = patient["id"]

        # Update Demographics Banner
        demo_str = (
            f"IDENTIFIER: {patient['patient_uid']}   |   NAME: {patient['full_name']}   |   "
            f"AGE: {patient['age']} yrs ({patient['gender']})   |   BLOOD GROUP: {patient['blood_group']}   |   "
            f"PHONE: {patient['phone']}   |   EMERGENCY CONTACT: {patient['emergency_contact']}"
        )
        self.lbl_demographics.configure(text=demo_str, fg=config.ACCENT_CYAN)

        # Load Encounters
        for row in self.tree_history.get_children():
            self.tree_history.delete(row)

        history_rows = db.get_patient_medical_history(patient["id"])
        for h in history_rows:
            self.tree_history.insert("", tk.END, values=(
                h["id"],
                h["visit_date"],
                h["doctor_name"] or "Specialist",
                h["specialization"] or "Clinical Dept",
                h["diagnosis"],
                h["treatment"],
                h["prescriptions"]
            ))

        if history_rows:
            first_child = self.tree_history.get_children()[0]
            self.tree_history.selection_set(first_child)
            self._on_encounter_selected()
        else:
            self.txt_detail.configure(state="normal")
            self.txt_detail.delete("1.0", tk.END)
            self.txt_detail.insert(tk.END, "No recorded clinical visits found for this patient.")
            self.txt_detail.configure(state="disabled")

    def _on_encounter_selected(self, event=None):
        selected = self.tree_history.selection()
        if not selected:
            return

        item_vals = self.tree_history.item(selected[0])["values"]
        history_id = int(item_vals[0])

        # Fetch detail from database
        history_rows = db.get_patient_medical_history(self.selected_patient_id)
        enc = None
        for r in history_rows:
            if r["id"] == history_id:
                enc = r
                break

        if not enc:
            return

        detail_text = (
            f"◈ ENCOUNTER IDENTIFIER: REC-{enc['id']:04d}           VISIT DATE: {enc['visit_date']}\n"
            f"◈ ATTENDING PHYSICIAN : {enc['doctor_name']} ({enc['specialization']})\n"
            f"--------------------------------------------------------------------------\n"
            f"1. CLINICAL DIAGNOSIS NOTES:\n   {enc['diagnosis']}\n\n"
            f"2. MEDICAL TREATMENT & PROCEDURES PERFORMED:\n   {enc['treatment']}\n\n"
            f"3. PRESCRIBED PHARMACEUTICALS & REGIMEN:\n   {enc['prescriptions']}\n\n"
            f"4. ADMINISTRATIVE / FOLLOW-UP REMARKS:\n   {enc.get('notes', 'None recorded.')}\n"
            f"--------------------------------------------------------------------------\n"
            f"LOG TIMESTAMP: {enc['created_at']}   |   RECORD VALIDATED: J.A.R.V.I.S. QUANTUM EHR"
        )

        self.txt_detail.configure(state="normal")
        self.txt_detail.delete("1.0", tk.END)
        self.txt_detail.insert(tk.END, detail_text)
        self.txt_detail.configure(state="disabled")

    def _open_add_encounter_modal(self):
        if not self.selected_patient_id:
            messagebox.showwarning("Selection Required", "Please select a patient first.")
            return
        AddEncounterModal(self, patient_id=self.selected_patient_id, on_save_callback=self._on_patient_selected)


class AddEncounterModal(tk.Toplevel):
    """
    Modal to append an administrative clinical encounter log to a patient's dossier.
    """

    def __init__(self, parent, patient_id: int, on_save_callback=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.on_save_callback = on_save_callback

        self.title("MEDNOVA AI — RECORD CLINICAL ENCOUNTER")
        self.geometry("640x600")
        self.configure(bg=config.BG_DARK)
        self.transient(parent)
        self.grab_set()

        self._center(640, 600)
        self.doctors_list = db.get_all_doctors()
        self.patient = db.get_patient_by_id(patient_id)

        self._build_ui()

    def _center(self, w, h):
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        container = tk.Frame(self, bg=config.BG_PANEL, highlightthickness=2, highlightbackground=config.ACCENT_CYAN)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=config.BG_DARK, height=50)
        header.pack(fill=tk.X)
        lbl_title = tk.Label(header, text=f"◈ LOG CLINICAL VISIT: {self.patient['full_name']}", font=config.FONT_SUBTITLE, fg=config.ACCENT_CYAN, bg=config.BG_DARK)
        lbl_title.pack(side=tk.LEFT, padx=16, pady=12)

        body = tk.Frame(container, bg=config.BG_PANEL)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Attending Doctor & Visit Date
        r0 = tk.Frame(body, bg=config.BG_PANEL)
        r0.pack(fill=tk.X, pady=6)

        f_doc = tk.Frame(r0, bg=config.BG_PANEL)
        f_doc.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_doc, text="ATTENDING PHYSICIAN *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        doc_opts = [f"{d['doctor_uid']} — {d['full_name']} ({d['specialization']})" for d in self.doctors_list]
        self.combo_doctor = ttk.Combobox(f_doc, values=doc_opts, state="readonly")
        if doc_opts:
            self.combo_doctor.set(doc_opts[0])
        self.combo_doctor.pack(fill=tk.X, ipady=4, pady=(3, 0))

        f_dt = tk.Frame(r0, bg=config.BG_PANEL)
        f_dt.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_dt, text="VISIT DATE (YYYY-MM-DD) *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_date = tk.Entry(f_dt, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_date.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        # Diagnosis Notes
        r1 = tk.Frame(body, bg=config.BG_PANEL)
        r1.pack(fill=tk.X, pady=6)
        tk.Label(r1, text="CLINICAL DIAGNOSIS NOTES *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_diag = tk.Entry(r1, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_diag.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_diag.insert(0, "Acute tension cephalea / fatigue; vitals stable")

        # Treatment & Procedures
        r2 = tk.Frame(body, bg=config.BG_PANEL)
        r2.pack(fill=tk.X, pady=6)
        tk.Label(r2, text="TREATMENT / PROCEDURES PERFORMED *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_treat = tk.Entry(r2, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_treat.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_treat.insert(0, "Hydration IV therapy & cranial ultrasound scan")

        # Prescriptions
        r3 = tk.Frame(body, bg=config.BG_PANEL)
        r3.pack(fill=tk.X, pady=6)
        tk.Label(r3, text="PRESCRIBED MEDICATIONS & DOSAGE *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_presc = tk.Entry(r3, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_presc.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_presc.insert(0, "Ibuprofen 400mg TID, Multivitamin tabs daily for 7 days")

        # Follow-up Instructions
        r4 = tk.Frame(body, bg=config.BG_PANEL)
        r4.pack(fill=tk.X, pady=6)
        tk.Label(r4, text="REMARKS & FOLLOW-UP SCHEDULE:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_notes = tk.Entry(r4, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_notes.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_notes.insert(0, "Follow-up consultation in 14 days if symptoms persist")

        # Footer Buttons
        btn_footer = tk.Frame(container, bg=config.BG_PANEL)
        btn_footer.pack(fill=tk.X, pady=(16, 16), padx=20)

        btn_save = GlowingButton(btn_footer, text="⚡ COMMIT ENCOUNTER TO DOSSIER", theme="cyan", command=self._save_encounter)
        btn_save.pack(side=tk.RIGHT, padx=6)

        btn_cancel = GlowingButton(btn_footer, text="✕ CANCEL", theme="ghost", command=self.destroy)
        btn_cancel.pack(side=tk.RIGHT)

    def _save_encounter(self):
        doc_idx = self.combo_doctor.current()
        date_str = self.entry_date.get().strip()
        diag = self.entry_diag.get().strip()
        treat = self.entry_treat.get().strip()
        presc = self.entry_presc.get().strip()
        notes = self.entry_notes.get().strip()

        if doc_idx < 0:
            messagebox.showerror("Error", "Please select an attending doctor.")
            return

        if not date_str or len(date_str) != 10:
            messagebox.showerror("Error", "Date must be YYYY-MM-DD.")
            return

        if not diag or not treat or not presc:
            messagebox.showerror("Error", "Diagnosis, Treatment, and Prescriptions are mandatory fields.")
            return

        doctor = self.doctors_list[doc_idx]
        encounter_data = {
            "patient_id": self.patient_id,
            "doctor_id": doctor["id"],
            "visit_date": date_str,
            "diagnosis": diag,
            "treatment": treat,
            "prescriptions": presc,
            "notes": notes,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        db.insert_medical_history(encounter_data)
        db.log_activity(
            current_session.user_id,
            "MEDICAL_HISTORY_ADD",
            f"Logged clinical encounter for {self.patient['full_name']} by {doctor['full_name']}."
        )
        messagebox.showinfo("Encounter Logged", "Clinical record successfully encrypted and appended to patient dossier.")

        if self.on_save_callback:
            self.on_save_callback()

        self.destroy()
