"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: billing.py
Description: Financial ledger & patient billing engine. Uses Python Decimal for
             zero-roundoff currency math, generates itemized ASCII holographic
             invoices, exports receipts, and tracks payment settlement lifecycles.
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from decimal import Decimal, ROUND_HALF_UP
import datetime
from pathlib import Path
import config
from database import db
from utils import (
    GlowingButton, create_holographic_card, format_currency,
    parse_decimal, generate_ascii_invoice_text, export_treeview_to_csv
)
from voice_engine import voice_assistant
from security import current_session


class BillingManagementView(tk.Frame):
    """
    Hospital Financial & Invoicing Command Screen.
    """

    def __init__(self, parent, navigation_controller):
        super().__init__(parent, bg=config.BG_DARK)
        self.nav = navigation_controller

        self._build_ui()
        self.load_bills()

    def _build_ui(self):
        self.main_container = tk.Frame(self, bg=config.BG_DARK)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # Header Control Bar
        header_card = create_holographic_card(self.main_container, title="HOSPITAL REVENUE & INVOICING COMMAND", subtitle="DECIMAL FINANCIAL ACCURACY")
        header_card.pack(fill=tk.X, pady=(0, 14))

        ctrl_frame = tk.Frame(header_card, bg=config.BG_CARD)
        ctrl_frame.pack(fill=tk.X, padx=14, pady=10)

        # Search
        lbl_search = tk.Label(ctrl_frame, text="QUERY INVOICES:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_CYAN, bg=config.BG_CARD)
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
        self.entry_search.bind("<KeyRelease>", lambda e: self.load_bills())

        # Payment Status Filter
        lbl_st = tk.Label(ctrl_frame, text="PAYMENT:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_CARD)
        lbl_st.pack(side=tk.LEFT, padx=(6, 6))

        self.combo_filter = ttk.Combobox(
            ctrl_frame,
            values=["All Statuses", "Paid", "Pending", "Overdue"],
            state="readonly",
            width=14
        )
        self.combo_filter.set("All Statuses")
        self.combo_filter.pack(side=tk.LEFT, padx=(0, 12))
        self.combo_filter.bind("<<ComboboxSelected>>", lambda e: self.load_bills())

        # Action Buttons
        btn_new = GlowingButton(ctrl_frame, text="➕ NEW INVOICE", theme="green", command=self._open_new_bill_modal)
        btn_new.pack(side=tk.LEFT, padx=3)

        btn_settle = GlowingButton(ctrl_frame, text="✓ MARK SETTLED", theme="cyan", command=self._mark_bill_paid)
        btn_settle.pack(side=tk.LEFT, padx=3)

        btn_view = GlowingButton(ctrl_frame, text="👁 PRINT / VIEW", theme="blue", command=self._view_invoice)
        btn_view.pack(side=tk.LEFT, padx=3)

        btn_export = GlowingButton(ctrl_frame, text="⭳ EXPORT CSV", theme="ghost", command=lambda: export_treeview_to_csv(self.tree, "hospital_bills_ledger.csv"))
        btn_export.pack(side=tk.RIGHT)

        # Table Container
        table_card = tk.Frame(self.main_container, bg=config.BG_CARD, highlightthickness=1, highlightbackground=config.ACCENT_BORDER)
        table_card.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "inv_no", "date", "patient", "consultation", "services", "tax", "total", "method", "status")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("inv_no", text="INVOICE NO")
        self.tree.heading("date", text="BILL DATE")
        self.tree.heading("patient", text="PATIENT RECIPIENT")
        self.tree.heading("consultation", text="CONSULTATION")
        self.tree.heading("services", text="SERVICES")
        self.tree.heading("tax", text="TAX %")
        self.tree.heading("total", text="TOTAL AMOUNT")
        self.tree.heading("method", text="PAYMENT METHOD")
        self.tree.heading("status", text="STATUS")

        self.tree.column("id", width=40, anchor=tk.CENTER)
        self.tree.column("inv_no", width=130, anchor=tk.CENTER)
        self.tree.column("date", width=95, anchor=tk.CENTER)
        self.tree.column("patient", width=180, anchor=tk.W)
        self.tree.column("consultation", width=110, anchor=tk.E)
        self.tree.column("services", width=110, anchor=tk.E)
        self.tree.column("tax", width=60, anchor=tk.CENTER)
        self.tree.column("total", width=120, anchor=tk.E)
        self.tree.column("method", width=120, anchor=tk.CENTER)
        self.tree.column("status", width=95, anchor=tk.CENTER)

        scrollbar_y = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y, pady=8, padx=(0, 8))

        self.tree.bind("<Double-1>", lambda e: self._view_invoice())

    def load_bills(self):
        """Fetch bills from database and populate ledger table."""
        query = self.entry_search.get().strip()
        status_filter = self.combo_filter.get()
        bills = db.get_all_bills(status_filter=status_filter, search_query=query)

        for row in self.tree.get_children():
            self.tree.delete(row)

        for b in bills:
            self.tree.insert("", tk.END, values=(
                b["id"],
                b["invoice_no"],
                b["bill_date"],
                b["patient_name"],
                format_currency(b["consultation_fee"]),
                format_currency(b["service_charges"]),
                f"{b['tax_percent']:.1f}%",
                format_currency(b["total_amount"]),
                b["payment_method"],
                b["payment_status"]
            ))

    def _get_selected_bill(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an invoice from the ledger.")
            return None
        bill_id = int(self.tree.item(selected[0])["values"][0])
        for b in db.get_all_bills():
            if b["id"] == bill_id:
                return b
        return None

    def _open_new_bill_modal(self):
        GenerateBillModal(self, on_save_callback=self.load_bills)

    def _mark_bill_paid(self):
        bill = self._get_selected_bill()
        if not bill:
            return

        if bill["payment_status"] == "Paid":
            messagebox.showinfo("Already Settled", f"Invoice {bill['invoice_no']} is already marked as Paid.")
            return

        confirm = messagebox.askyesno(
            "Confirm Settlement",
            f"Record complete settlement of {format_currency(bill['total_amount'])}\n"
            f"for Invoice {bill['invoice_no']} ({bill['patient_name']})?"
        )
        if confirm:
            db.update_bill_payment_status(bill["id"], "Paid", bill["payment_method"])
            db.log_activity(current_session.user_id, "BILL_PAID", f"Marked invoice {bill['invoice_no']} as Paid.")
            messagebox.showinfo("Payment Recorded", f"Invoice {bill['invoice_no']} successfully settled.")
            self.load_bills()

    def _view_invoice(self):
        bill = self._get_selected_bill()
        if not bill:
            return
        patient = db.get_patient_by_id(bill["patient_id"])
        ViewInvoiceModal(self, bill_data=bill, patient_data=patient)


class GenerateBillModal(tk.Toplevel):
    """
    Modal Dialog to generate patient invoices with live Decimal calculation.
    """

    def __init__(self, parent, on_save_callback=None):
        super().__init__(parent)
        self.on_save_callback = on_save_callback

        self.title("MEDNOVA AI — FINANCIAL INVOICE DISPATCH")
        self.geometry("640x620")
        self.minsize(600, 580)
        self.configure(bg=config.BG_DARK)
        self.transient(parent)
        self.grab_set()

        self._center(640, 620)
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

        header = tk.Frame(container, bg=config.BG_DARK, height=50)
        header.pack(fill=tk.X)
        lbl_title = tk.Label(header, text="◈ GENERATE CLINICAL BILLING INVOICE", font=config.FONT_SUBTITLE, fg=config.ACCENT_CYAN, bg=config.BG_DARK)
        lbl_title.pack(side=tk.LEFT, padx=16, pady=12)

        body = tk.Frame(container, bg=config.BG_PANEL)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Invoice No & Date
        r0 = tk.Frame(body, bg=config.BG_PANEL)
        r0.pack(fill=tk.X, pady=6)

        self.inv_no = db.get_next_invoice_no()
        f_inv = tk.Frame(r0, bg=config.BG_PANEL)
        f_inv.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_inv, text="INVOICE NUMBER:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_inv = tk.Entry(f_inv, bg=config.BG_CARD, fg=config.ACCENT_CYAN, font=config.FONT_BODY_BOLD, relief=tk.FLAT)
        self.entry_inv.insert(0, self.inv_no)
        self.entry_inv.configure(state="readonly")
        self.entry_inv.pack(fill=tk.X, ipady=6, pady=(3, 0))

        f_dt = tk.Frame(r0, bg=config.BG_PANEL)
        f_dt.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_dt, text="BILLING DATE (YYYY-MM-DD):", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_date = tk.Entry(f_dt, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_date.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        # Select Patient
        r1 = tk.Frame(body, bg=config.BG_PANEL)
        r1.pack(fill=tk.X, pady=6)
        tk.Label(r1, text="PATIENT RECIPIENT *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        pat_opts = [f"{p['patient_uid']} — {p['full_name']} (Blood: {p['blood_group']})" for p in self.patients_list]
        self.combo_patient = ttk.Combobox(r1, values=pat_opts, state="readonly")
        if pat_opts:
            self.combo_patient.set(pat_opts[0])
        self.combo_patient.pack(fill=tk.X, ipady=4, pady=(3, 0))

        # Financial Inputs (Consultation & Service Charges)
        r2 = tk.Frame(body, bg=config.BG_PANEL)
        r2.pack(fill=tk.X, pady=6)

        f_con = tk.Frame(r2, bg=config.BG_PANEL)
        f_con.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_con, text="CONSULTATION CHARGES ($) *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_consult = tk.Entry(f_con, bg=config.BG_INPUT, fg=config.ACCENT_GREEN, font=config.FONT_BODY_BOLD, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_consult.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_consult.insert(0, "200.00")
        self.entry_consult.bind("<KeyRelease>", self._recalc_total)

        f_srv = tk.Frame(r2, bg=config.BG_PANEL)
        f_srv.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_srv, text="ADDITIONAL SERVICES / LABS ($):", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_services = tk.Entry(f_srv, bg=config.BG_INPUT, fg=config.ACCENT_GREEN, font=config.FONT_BODY_BOLD, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_services.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_services.insert(0, "75.00")
        self.entry_services.bind("<KeyRelease>", self._recalc_total)

        # Tax Percent & Calculated Total Display
        r3 = tk.Frame(body, bg=config.BG_PANEL)
        r3.pack(fill=tk.X, pady=6)

        f_tax = tk.Frame(r3, bg=config.BG_PANEL)
        f_tax.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_tax, text="HEALTHCARE SURCHARGE / TAX (%):", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_tax = tk.Entry(f_tax, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_tax.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_tax.insert(0, "5.0")
        self.entry_tax.bind("<KeyRelease>", self._recalc_total)

        f_tot = tk.Frame(r3, bg=config.BG_PANEL)
        f_tot.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_tot, text="NET TOTAL (DECIMAL VERIFIED):", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_CYAN, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.lbl_total_display = tk.Label(f_tot, text="$288.75", font=config.FONT_TITLE, fg=config.ACCENT_CYAN, bg=config.BG_CARD)
        self.lbl_total_display.pack(fill=tk.X, ipady=4, pady=(3, 0))

        # Payment Status & Method
        r4 = tk.Frame(body, bg=config.BG_PANEL)
        r4.pack(fill=tk.X, pady=6)

        f_status = tk.Frame(r4, bg=config.BG_PANEL)
        f_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_status, text="SETTLEMENT STATUS *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.combo_status = ttk.Combobox(f_status, values=["Paid", "Pending", "Overdue"], state="readonly")
        self.combo_status.set("Pending")
        self.combo_status.pack(fill=tk.X, ipady=4, pady=(3, 0))

        f_mth = tk.Frame(r4, bg=config.BG_PANEL)
        f_mth.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(f_mth, text="PAYMENT METHOD *:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.combo_method = ttk.Combobox(f_mth, values=["Cash", "Credit Card", "Quantum Wire / UPI", "Health Insurance"], state="readonly")
        self.combo_method.set("Credit Card")
        self.combo_method.pack(fill=tk.X, ipady=4, pady=(3, 0))

        # Clinical Notes
        r5 = tk.Frame(body, bg=config.BG_PANEL)
        r5.pack(fill=tk.X, pady=6)
        tk.Label(r5, text="INVOICE DESCRIPTION / CLINICAL NOTES:", font=config.FONT_CARD_LABEL, fg=config.COLOR_TEXT_SECONDARY, bg=config.BG_PANEL).pack(anchor=tk.W)
        self.entry_notes = tk.Entry(r5, bg=config.BG_INPUT, fg=config.COLOR_TEXT_PRIMARY, font=config.FONT_BODY, insertbackground=config.ACCENT_CYAN, relief=tk.FLAT)
        self.entry_notes.pack(fill=tk.X, ipady=6, pady=(3, 0))
        self.entry_notes.insert(0, "Specialist diagnostic consultation & lab analysis")

        # Footer Buttons
        btn_footer = tk.Frame(container, bg=config.BG_PANEL)
        btn_footer.pack(fill=tk.X, pady=(16, 16), padx=20)

        btn_save = GlowingButton(btn_footer, text="⚡ ISSUE INVOICE", theme="cyan", command=self._issue_invoice)
        btn_save.pack(side=tk.RIGHT, padx=6)

        btn_cancel = GlowingButton(btn_footer, text="✕ CANCEL", theme="ghost", command=self.destroy)
        btn_cancel.pack(side=tk.RIGHT)

        self._recalc_total()

    def _calculate_amounts(self):
        valid1, con_dec = parse_decimal(self.entry_consult.get())
        valid2, srv_dec = parse_decimal(self.entry_services.get())
        valid3, tax_dec = parse_decimal(self.entry_tax.get())

        if not (valid1 and valid2 and valid3):
            return None, None, None, None

        subtotal = con_dec + srv_dec
        tax_amount = (subtotal * tax_dec) / Decimal("100")
        total = (subtotal + tax_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return con_dec, srv_dec, tax_dec, total

    def _recalc_total(self, event=None):
        con_dec, srv_dec, tax_dec, total = self._calculate_amounts()
        if total is not None:
            self.lbl_total_display.configure(text=format_currency(total), fg=config.ACCENT_CYAN)
        else:
            self.lbl_total_display.configure(text="SYNTAX ERROR", fg=config.ACCENT_DANGER)

    def _issue_invoice(self):
        pat_idx = self.combo_patient.current()
        if pat_idx < 0:
            messagebox.showerror("Error", "Please select a patient.")
            return

        con_dec, srv_dec, tax_dec, total = self._calculate_amounts()
        if total is None:
            messagebox.showerror("Math Error", "Invalid numeric values in financial charge inputs.")
            return

        patient = self.patients_list[pat_idx]
        bill_date = self.entry_date.get().strip()
        status = self.combo_status.get().strip()
        method = self.combo_method.get().strip()
        notes = self.entry_notes.get().strip()

        bill_dict = {
            "invoice_no": self.inv_no,
            "patient_id": patient["id"],
            "appointment_id": None,
            "consultation_fee": float(con_dec),
            "service_charges": float(srv_dec),
            "tax_percent": float(tax_dec),
            "total_amount": float(total),
            "payment_status": status,
            "bill_date": bill_date,
            "payment_method": method,
            "notes": notes
        }

        db.insert_bill(bill_dict)
        db.log_activity(
            current_session.user_id,
            "BILL_CREATE",
            f"Generated invoice {self.inv_no} for {patient['full_name']} totaling {format_currency(total)}."
        )

        voice_assistant.announce_bill_generated(self.inv_no, format_currency(total))
        messagebox.showinfo("Invoice Issued", f"Invoice {self.inv_no} successfully logged in financial registry.")

        if self.on_save_callback:
            self.on_save_callback()

        self.destroy()


class ViewInvoiceModal(tk.Toplevel):
    """
    Futuristic Modal displaying an itemized printable holographic medical bill.
    """

    def __init__(self, parent, bill_data: dict, patient_data: dict):
        super().__init__(parent)
        self.bill = bill_data
        self.patient = patient_data or {"full_name": "N/A", "patient_uid": "N/A", "age": "N/A", "gender": "N/A", "blood_group": "N/A", "emergency_contact": "N/A"}

        self.title(f"MEDNOVA AI — INVOICE: {self.bill['invoice_no']}")
        self.geometry("740x660")
        self.configure(bg=config.BG_DARK)
        self.transient(parent)

        self._center(740, 660)
        self._build_ui()

    def _center(self, w, h):
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        container = tk.Frame(self, bg=config.BG_PANEL, highlightthickness=2, highlightbackground=config.ACCENT_CYAN)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=config.BG_DARK, height=45)
        header.pack(fill=tk.X)
        tk.Label(header, text=f"◈ HOLOGRAPHIC RECEIPT // {self.bill['invoice_no']}", font=config.FONT_SUBTITLE, fg=config.ACCENT_CYAN, bg=config.BG_DARK).pack(side=tk.LEFT, padx=16, pady=10)

        # ASCII formatted invoice in monospace text widget
        txt_frame = tk.Frame(container, bg=config.BG_CARD)
        txt_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=10)

        self.txt_invoice = tk.Text(
            txt_frame,
            bg=config.BG_INPUT,
            fg=config.ACCENT_CYAN,
            font=config.FONT_MONO,
            relief=tk.FLAT,
            padx=12,
            pady=10
        )
        self.txt_invoice.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(txt_frame, orient=tk.VERTICAL, command=self.txt_invoice.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_invoice.configure(yscrollcommand=scrollbar.set)

        # Generate invoice text
        self.invoice_text = generate_ascii_invoice_text(self.bill, self.patient)
        self.txt_invoice.insert(tk.END, self.invoice_text)
        self.txt_invoice.configure(state="disabled")

        # Footer Buttons
        footer = tk.Frame(container, bg=config.BG_PANEL)
        footer.pack(fill=tk.X, pady=(10, 14), padx=16)

        btn_save = GlowingButton(footer, text="💾 SAVE TO DISK (.TXT)", theme="cyan", command=self._save_to_disk)
        btn_save.pack(side=tk.RIGHT, padx=6)

        btn_close = GlowingButton(footer, text="✕ CLOSE", theme="ghost", command=self.destroy)
        btn_close.pack(side=tk.RIGHT)

    def _save_to_disk(self):
        target_path = config.INVOICES_DIR / f"{self.bill['invoice_no']}.txt"
        filepath = filedialog.asksaveasfilename(
            initialdir=str(config.INVOICES_DIR),
            initialfile=f"{self.bill['invoice_no']}.txt",
            defaultextension=".txt",
            filetypes=[("Text Receipt", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.invoice_text)
            messagebox.showinfo("Receipt Saved", f"Invoice saved to disk:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not write receipt to disk:\n{e}")
