"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: database.py
Description: SQLite3 database engine, schema migration, parameterized CRUD queries,
             relational integrity, and realistic demo dataset initialization.
=============================================================================
"""

import sqlite3
import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
import config
from security import hash_password


class DatabaseManager:
    """
    Central database manager for MEDNOVA AI.
    Handles connections, schema setup, transactions, and parameterized queries.
    """

    def __init__(self, db_path: str = None):
        self.db_path = str(db_path or config.DATABASE_PATH)
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection with foreign keys enabled and Row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_database(self):
        """Create all required tables and populate initial demo data if empty."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Users Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'Active'
            );
            """)

            # 2. Patients Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_uid TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                dob TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                blood_group TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                address TEXT,
                emergency_contact TEXT NOT NULL,
                registered_at TEXT NOT NULL,
                status TEXT DEFAULT 'Active'
            );
            """)

            # 3. Doctors Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_uid TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                qualification TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                room_no TEXT NOT NULL,
                visiting_hours TEXT NOT NULL,
                fee REAL NOT NULL,
                status TEXT DEFAULT 'Available'
            );
            """)

            # 4. Appointments Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_uid TEXT UNIQUE NOT NULL,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT DEFAULT 'Scheduled',
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
            );
            """)

            # 5. Medical History Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER,
                visit_date TEXT NOT NULL,
                diagnosis TEXT NOT NULL,
                treatment TEXT NOT NULL,
                prescriptions TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE SET NULL
            );
            """)

            # 6. Bills Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE NOT NULL,
                patient_id INTEGER NOT NULL,
                appointment_id INTEGER,
                consultation_fee REAL NOT NULL DEFAULT 0.0,
                service_charges REAL NOT NULL DEFAULT 0.0,
                tax_percent REAL NOT NULL DEFAULT 0.0,
                total_amount REAL NOT NULL DEFAULT 0.0,
                payment_status TEXT DEFAULT 'Pending',
                bill_date TEXT NOT NULL,
                payment_method TEXT DEFAULT 'Cash',
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL
            );
            """)

            # 7. Activity Logs Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );
            """)

            conn.commit()

        # Seed initial demo data if database is fresh
        self._seed_demo_data()

    def _seed_demo_data(self):
        """Populate database with rich J.A.R.V.I.S.-style hospital demo records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if users already seeded
            cursor.execute("SELECT COUNT(*) FROM users;")
            if cursor.fetchone()[0] > 0:
                return

            timestamp_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            today_str = datetime.date.today().strftime("%Y-%m-%d")

            # 1. Seed Demo Users
            users_data = [
                ("admin", "admin123", "Chief Director Tony Stark", config.ROLE_ADMIN, "director.stark@mednova.ai", "+1-800-555-0100"),
                ("dr_tony", "stark123", "Dr. Tony Stark, MD, PhD", config.ROLE_DOCTOR, "tony.stark@mednova.ai", "+1-800-555-0101"),
                ("dr_banner", "banner123", "Dr. Bruce Banner, MD, PhD", config.ROLE_DOCTOR, "bruce.banner@mednova.ai", "+1-800-555-0102"),
                ("dr_strange", "strange123", "Dr. Stephen Strange, MD", config.ROLE_DOCTOR, "stephen.strange@mednova.ai", "+1-800-555-0103"),
                ("recep_pepper", "pepper123", "Ms. Pepper Potts", config.ROLE_RECEPTIONIST, "pepper.potts@mednova.ai", "+1-800-555-0104")
            ]
            for username, raw_pass, full_name, role, email, phone in users_data:
                pwd_hash, salt = hash_password(raw_pass)
                cursor.execute("""
                    INSERT INTO users (username, password_hash, salt, full_name, role, email, phone, created_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Active');
                """, (username, pwd_hash, salt, full_name, role, email, phone, timestamp_now))

            # 2. Seed Doctors
            doctors_data = [
                ("MED-D-101", "Dr. Tony Stark, MD, PhD", "Neuro-Surgery & AI Brain Mapping", "MD, PhD - MIT Medical", "+1-800-555-0101", "tony.stark@mednova.ai", "Suite 401 (Quantum Lab)", "09:00 AM - 01:00 PM", 250.00, "Available"),
                ("MED-D-102", "Dr. Bruce Banner, MD, PhD", "Internal Medicine & Diagnostics", "MD, PhD - Harvard Medical", "+1-800-555-0102", "bruce.banner@mednova.ai", "Room 205 (Diagnostics Wing)", "10:00 AM - 02:00 PM", 180.00, "Available"),
                ("MED-D-103", "Dr. Stephen Strange, MD", "Orthopedic Surgery & Bio-prosthetics", "MD - Columbia Physicians", "+1-800-555-0103", "stephen.strange@mednova.ai", "Suite 310 (Surgical Bay)", "11:00 AM - 04:00 PM", 220.00, "In Consultation"),
                ("MED-D-104", "Dr. Helen Cho, MD, PhD", "Cardiovascular & Thoracic Surgery", "MD - Seoul National / Johns Hopkins", "+1-800-555-0105", "helen.cho@mednova.ai", "Suite 502 (Regen Wing)", "09:00 AM - 03:00 PM", 260.00, "Available"),
                ("MED-D-105", "Dr. Christine Palmer, MD", "Trauma & Emergency Care", "MD - Metro General", "+1-800-555-0106", "christine.palmer@mednova.ai", "ER-01 (Rapid Trauma)", "08:00 AM - 08:00 PM", 150.00, "Available")
            ]
            cursor.executemany("""
                INSERT INTO doctors (doctor_uid, full_name, specialization, qualification, phone, email, room_no, visiting_hours, fee, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, doctors_data)

            # 3. Seed Patients
            patients_data = [
                ("MED-P-2026-001", "Peter Parker", "2004-08-10", 22, "Male", "O+", "+1-555-0111", "peter.parker@dailybugle.com", "Queens, New York", "May Parker (+1-555-0112)", "2026-01-15 09:30:00", "Active"),
                ("MED-P-2026-002", "Natasha Romanoff", "1992-12-03", 34, "Female", "A-", "+1-555-0121", "n.romanoff@shield.gov", "New York City, NY", "Clint Barton (+1-555-0122)", "2026-01-18 11:20:00", "Active"),
                ("MED-P-2026-003", "Col. James Rhodes", "1981-10-06", 45, "Male", "O+", "+1-555-0131", "j.rhodes@usaf.mil", "Arlington, VA", "Carol Danvers (+1-555-0132)", "2026-01-22 14:10:00", "Active"),
                ("MED-P-2026-004", "Wanda Maximoff", "1997-02-10", 29, "Female", "AB+", "+1-555-0141", "w.maximoff@avengers.org", "Westview, NJ", "Vision (+1-555-0142)", "2026-02-01 10:00:00", "Active"),
                ("MED-P-2026-005", "Sam Wilson", "1988-09-23", 38, "Male", "B+", "+1-555-0151", "sam.wilson@airforce.mil", "Delacroix, LA", "Sarah Wilson (+1-555-0152)", "2026-02-05 16:45:00", "Active"),
                ("MED-P-2026-006", "Carol Danvers", "1990-04-24", 36, "Female", "B-", "+1-555-0161", "c.danvers@starforce.space", "Boston, MA", "Maria Rambeau (+1-555-0162)", "2026-02-10 13:15:00", "Active")
            ]
            cursor.executemany("""
                INSERT INTO patients (patient_uid, full_name, dob, age, gender, blood_group, phone, email, address, emergency_contact, registered_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, patients_data)

            # 4. Seed Appointments
            tomorrow_str = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            appointments_data = [
                ("APT-2026-001", 1, 1, today_str, "09:30 AM", "Neural sync check & reflex testing", "Scheduled", "Patient reports mild sensory overload", timestamp_now),
                ("APT-2026-002", 2, 2, today_str, "10:30 AM", "Comprehensive cellular toxin screening", "Scheduled", "Routine bi-annual executive checkup", timestamp_now),
                ("APT-2026-003", 3, 3, today_str, "11:00 AM", "Cybernetic exoskeleton spinal calibration", "In Progress", "Review lumbar sensor telemetries", timestamp_now),
                ("APT-2026-004", 4, 1, tomorrow_str, "10:00 AM", "Synaptic resonance & EEG mapping", "Scheduled", "Electrophysiological scan scheduled", timestamp_now),
                ("APT-2026-005", 5, 4, tomorrow_str, "01:30 PM", "High-altitude pulmonary capacity test", "Scheduled", "Aviation endurance assessment", timestamp_now),
                ("APT-2026-006", 6, 2, "2026-02-14", "11:30 AM", "Cosmic radiation metabolic scan", "Completed", "Metabolic parameters fully stabilized", timestamp_now),
            ]
            cursor.executemany("""
                INSERT INTO appointments (appointment_uid, patient_id, doctor_id, appointment_date, appointment_time, reason, status, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, appointments_data)

            # 5. Seed Medical History
            history_data = [
                (1, 1, "2026-01-20", "Spider-Sense Acuity Syndrome", "Sensory damper recalibration", "Omega-3 NeuroGel 500mg daily", "Vitals optimal; rapid cellular regeneration noted.", timestamp_now),
                (3, 3, "2026-01-25", "Lower Lumbar Biomechanical Strain", "L4-L5 Exoskeleton brace realigned", "Muscle relaxant, Cryo-therapy 20 min", "Mobility improved by 28%. Continue physical therapy.", timestamp_now),
                (4, 1, "2026-02-05", "Elevated Bio-synaptic Energy Output", "Deep neural harmonic meditation", "Neuro-calm electrolyte tonic", "Psychological evaluation shows stable mental equilibrium.", timestamp_now),
                (6, 2, "2026-02-14", "Photon Metabolic Hyper-absorption", "Cellular thermal cooling cycle", "Vitamin B-Complex, High hydration", "No adverse cellular degradation detected.", timestamp_now),
            ]
            cursor.executemany("""
                INSERT INTO medical_history (patient_id, doctor_id, visit_date, diagnosis, treatment, prescriptions, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, history_data)

            # 6. Seed Bills
            bills_data = [
                ("INV-2026-1001", 1, 1, 250.00, 150.00, 5.0, 420.00, "Paid", today_str, "Credit Card", "Full settlement received"),
                ("INV-2026-1002", 2, 2, 180.00, 320.00, 5.0, 525.00, "Paid", today_str, "Quantum Wire", "Covered via S.H.I.E.L.D. Insurance"),
                ("INV-2026-1003", 3, 3, 220.00, 500.00, 5.0, 756.00, "Pending", today_str, "Health Insurance", "Pending military defense claim clearance"),
                ("INV-2026-1004", 4, 4, 250.00, 100.00, 5.0, 367.50, "Pending", tomorrow_str, "Cash", "Pre-admission advance billing"),
                ("INV-2026-1005", 6, 2, 180.00, 450.00, 5.0, 661.50, "Paid", "2026-02-14", "Credit Card", "Settled at counter"),
            ]
            cursor.executemany("""
                INSERT INTO bills (invoice_no, patient_id, appointment_id, consultation_fee, service_charges, tax_percent, total_amount, payment_status, bill_date, payment_method, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, bills_data)

            # 7. Seed Activity Logs
            logs_data = [
                (1, "SYSTEM_BOOT", "MEDNOVA AI Quantum Core initialized with full database integrity.", timestamp_now),
                (1, "USER_LOGIN", "Chief Director Tony Stark authenticated into Command Console.", timestamp_now),
                (5, "PATIENT_REGISTER", "Registered new patient Col. James Rhodes (MED-P-2026-003).", timestamp_now),
                (5, "BILL_GENERATE", "Generated invoice INV-2026-1001 for Peter Parker.", timestamp_now),
            ]
            cursor.executemany("""
                INSERT INTO activity_logs (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?);
            """, logs_data)

            conn.commit()

    # =========================================================================
    # USER & AUTHENTICATION CRUD
    # =========================================================================
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetch user record by unique username."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND status = 'Active';", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_user_password(self, user_id: int, new_password_hash: str, new_salt: str) -> bool:
        """Update password hash and salt for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET password_hash = ?, salt = ? WHERE id = ?;
            """, (new_password_hash, new_salt, user_id))
            conn.commit()
            return cursor.rowcount > 0

    # =========================================================================
    # DASHBOARD KPI & STATS
    # =========================================================================
    def get_dashboard_kpis(self) -> Dict[str, Any]:
        """Retrieve real-time consolidated KPI statistics for the central dashboard."""
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Total Patients
            cursor.execute("SELECT COUNT(*) FROM patients WHERE status = 'Active';")
            total_patients = cursor.fetchone()[0]

            # 2. Total Doctors
            cursor.execute("SELECT COUNT(*) FROM doctors;")
            total_doctors = cursor.fetchone()[0]

            # 3. Today's Appointments
            cursor.execute("SELECT COUNT(*) FROM appointments WHERE appointment_date = ?;", (today_str,))
            today_appointments = cursor.fetchone()[0]

            # 4. Total Completed Appointments
            cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'Completed';")
            completed_appointments = cursor.fetchone()[0]

            # 5. Total Hospital Revenue (Paid bills)
            cursor.execute("SELECT COALESCE(SUM(total_amount), 0.0) FROM bills WHERE payment_status = 'Paid';")
            total_revenue = cursor.fetchone()[0]

            # 6. Pending Billing Amount
            cursor.execute("SELECT COALESCE(SUM(total_amount), 0.0) FROM bills WHERE payment_status = 'Pending';")
            pending_bills_amount = cursor.fetchone()[0]

            # 7. Available Doctors Count
            cursor.execute("SELECT COUNT(*) FROM doctors WHERE status = 'Available';")
            available_doctors = cursor.fetchone()[0]

            return {
                "total_patients": total_patients,
                "total_doctors": total_doctors,
                "today_appointments": today_appointments,
                "completed_appointments": completed_appointments,
                "total_revenue": total_revenue,
                "pending_bills_amount": pending_bills_amount,
                "available_doctors": available_doctors
            }

    # =========================================================================
    # PATIENT MANAGEMENT CRUD
    # =========================================================================
    def get_all_patients(self, search_query: str = "") -> List[Dict[str, Any]]:
        """Retrieve all active patients, optionally filtered by name, phone, or UID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if search_query.strip():
                pattern = f"%{search_query.strip()}%"
                cursor.execute("""
                    SELECT * FROM patients 
                    WHERE (full_name LIKE ? OR patient_uid LIKE ? OR phone LIKE ?)
                    ORDER BY id DESC;
                """, (pattern, pattern, pattern))
            else:
                cursor.execute("SELECT * FROM patients ORDER BY id DESC;")
            return [dict(row) for row in cursor.fetchall()]

    def get_patient_by_id(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """Fetch patient by internal database ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients WHERE id = ?;", (patient_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def insert_patient(self, data: Dict[str, Any]) -> int:
        """Insert a newly registered patient and return new row ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO patients (
                    patient_uid, full_name, dob, age, gender, blood_group,
                    phone, email, address, emergency_contact, registered_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                data["patient_uid"], data["full_name"], data["dob"], data["age"],
                data["gender"], data["blood_group"], data["phone"], data.get("email", ""),
                data.get("address", ""), data["emergency_contact"], data["registered_at"],
                data.get("status", "Active")
            ))
            conn.commit()
            return cursor.lastrowid

    def update_patient(self, patient_id: int, data: Dict[str, Any]) -> bool:
        """Update existing patient demographic details."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE patients SET
                    full_name = ?, dob = ?, age = ?, gender = ?, blood_group = ?,
                    phone = ?, email = ?, address = ?, emergency_contact = ?, status = ?
                WHERE id = ?;
            """, (
                data["full_name"], data["dob"], data["age"], data["gender"],
                data["blood_group"], data["phone"], data.get("email", ""),
                data.get("address", ""), data["emergency_contact"], data.get("status", "Active"),
                patient_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_patient(self, patient_id: int) -> bool:
        """Cascade delete patient record from database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM patients WHERE id = ?;", (patient_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_next_patient_uid(self) -> str:
        """Generate the next unique Patient UID string."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(id) FROM patients;")
            max_id = cursor.fetchone()[0] or 0
            year = datetime.date.today().year
            return f"MED-P-{year}-{max_id + 1:04d}"

    # =========================================================================
    # DOCTOR MANAGEMENT CRUD
    # =========================================================================
    def get_all_doctors(self, search_query: str = "", spec_filter: str = "") -> List[Dict[str, Any]]:
        """Retrieve doctors, filtered optionally by name/uid and specialization."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM doctors WHERE 1=1"
            params = []

            if search_query.strip():
                query += " AND (full_name LIKE ? OR doctor_uid LIKE ? OR room_no LIKE ?)"
                pattern = f"%{search_query.strip()}%"
                params.extend([pattern, pattern, pattern])

            if spec_filter and spec_filter != "All Specializations":
                query += " AND specialization = ?"
                params.append(spec_filter)

            query += " ORDER BY id ASC;"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_doctor_by_id(self, doctor_id: int) -> Optional[Dict[str, Any]]:
        """Fetch doctor record by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM doctors WHERE id = ?;", (doctor_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def insert_doctor(self, data: Dict[str, Any]) -> int:
        """Insert a new doctor profile into database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO doctors (
                    doctor_uid, full_name, specialization, qualification,
                    phone, email, room_no, visiting_hours, fee, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                data["doctor_uid"], data["full_name"], data["specialization"],
                data["qualification"], data["phone"], data.get("email", ""),
                data["room_no"], data["visiting_hours"], float(data["fee"]),
                data.get("status", "Available")
            ))
            conn.commit()
            return cursor.lastrowid

    def update_doctor(self, doctor_id: int, data: Dict[str, Any]) -> bool:
        """Update doctor credentials and schedule."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE doctors SET
                    full_name = ?, specialization = ?, qualification = ?,
                    phone = ?, email = ?, room_no = ?, visiting_hours = ?,
                    fee = ?, status = ?
                WHERE id = ?;
            """, (
                data["full_name"], data["specialization"], data["qualification"],
                data["phone"], data.get("email", ""), data["room_no"],
                data["visiting_hours"], float(data["fee"]), data.get("status", "Available"),
                doctor_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_doctor(self, doctor_id: int) -> bool:
        """Delete doctor record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM doctors WHERE id = ?;", (doctor_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_next_doctor_uid(self) -> str:
        """Generate next sequential Doctor UID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(id) FROM doctors;")
            max_id = cursor.fetchone()[0] or 0
            return f"MED-D-{100 + max_id + 1}"

    # =========================================================================
    # APPOINTMENT MANAGEMENT CRUD & CONFLICT CHECKING
    # =========================================================================
    def check_appointment_conflict(self, doctor_id: int, appointment_date: str, appointment_time: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if the doctor already has an active (non-cancelled) booking
        at the specified date and time.
        Returns True if a conflict exists, False if slot is available.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT COUNT(*) FROM appointments
                WHERE doctor_id = ? 
                  AND appointment_date = ? 
                  AND appointment_time = ? 
                  AND status != 'Cancelled'
            """
            params = [doctor_id, appointment_date, appointment_time]
            if exclude_id is not None:
                query += " AND id != ?"
                params.append(exclude_id)

            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            return count > 0

    def get_all_appointments(self, status_filter: str = "", date_filter: str = "", search_query: str = "") -> List[Dict[str, Any]]:
        """Retrieve enriched appointments joined with patient and doctor details."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    a.*,
                    p.full_name AS patient_name,
                    p.patient_uid,
                    p.phone AS patient_phone,
                    d.full_name AS doctor_name,
                    d.specialization,
                    d.room_no,
                    d.fee AS consultation_fee
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                JOIN doctors d ON a.doctor_id = d.id
                WHERE 1=1
            """
            params = []

            if status_filter and status_filter != "All Statuses":
                query += " AND a.status = ?"
                params.append(status_filter)

            if date_filter:
                query += " AND a.appointment_date = ?"
                params.append(date_filter)

            if search_query.strip():
                pattern = f"%{search_query.strip()}%"
                query += " AND (p.full_name LIKE ? OR d.full_name LIKE ? OR a.appointment_uid LIKE ?)"
                params.extend([pattern, pattern, pattern])

            query += " ORDER BY a.appointment_date ASC, a.appointment_time ASC;"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def insert_appointment(self, data: Dict[str, Any]) -> int:
        """Book a new patient appointment."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO appointments (
                    appointment_uid, patient_id, doctor_id, appointment_date,
                    appointment_time, reason, status, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                data["appointment_uid"], data["patient_id"], data["doctor_id"],
                data["appointment_date"], data["appointment_time"], data["reason"],
                data.get("status", "Scheduled"), data.get("notes", ""),
                data["created_at"]
            ))
            conn.commit()
            return cursor.lastrowid

    def update_appointment_status(self, appointment_id: int, new_status: str) -> bool:
        """Update appointment progress status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE appointments SET status = ? WHERE id = ?;", (new_status, appointment_id))
            conn.commit()
            return cursor.rowcount > 0

    def reschedule_appointment(self, appointment_id: int, new_date: str, new_time: str, notes: str = "") -> bool:
        """Reschedule date and time of an existing appointment."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE appointments 
                SET appointment_date = ?, appointment_time = ?, notes = notes || ' ' || ?, status = 'Scheduled'
                WHERE id = ?;
            """, (new_date, new_time, notes, appointment_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_appointment(self, appointment_id: int) -> bool:
        """Delete appointment."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM appointments WHERE id = ?;", (appointment_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_next_appointment_uid(self) -> str:
        """Generate next sequential Appointment UID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(id) FROM appointments;")
            max_id = cursor.fetchone()[0] or 0
            year = datetime.date.today().year
            return f"APT-{year}-{max_id + 1:04d}"

    # =========================================================================
    # MEDICAL HISTORY CRUD
    # =========================================================================
    def get_patient_medical_history(self, patient_id: int) -> List[Dict[str, Any]]:
        """Retrieve all chronological clinical encounter notes for a patient."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    mh.*,
                    d.full_name AS doctor_name,
                    d.specialization
                FROM medical_history mh
                LEFT JOIN doctors d ON mh.doctor_id = d.id
                WHERE mh.patient_id = ?
                ORDER BY mh.visit_date DESC, mh.id DESC;
            """, (patient_id,))
            return [dict(row) for row in cursor.fetchall()]

    def insert_medical_history(self, data: Dict[str, Any]) -> int:
        """Record an administrative medical history log."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO medical_history (
                    patient_id, doctor_id, visit_date, diagnosis,
                    treatment, prescriptions, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                data["patient_id"], data.get("doctor_id"), data["visit_date"],
                data["diagnosis"], data["treatment"], data["prescriptions"],
                data.get("notes", ""), data["created_at"]
            ))
            conn.commit()
            return cursor.lastrowid

    # =========================================================================
    # BILLING & FINANCIAL MANAGEMENT CRUD
    # =========================================================================
    def get_all_bills(self, status_filter: str = "", search_query: str = "") -> List[Dict[str, Any]]:
        """Retrieve all billing invoices with patient linkage."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    b.*,
                    p.full_name AS patient_name,
                    p.patient_uid,
                    p.phone AS patient_phone
                FROM bills b
                JOIN patients p ON b.patient_id = p.id
                WHERE 1=1
            """
            params = []

            if status_filter and status_filter != "All Statuses":
                query += " AND b.payment_status = ?"
                params.append(status_filter)

            if search_query.strip():
                pattern = f"%{search_query.strip()}%"
                query += " AND (b.invoice_no LIKE ? OR p.full_name LIKE ? OR p.patient_uid LIKE ?)"
                params.extend([pattern, pattern, pattern])

            query += " ORDER BY b.id DESC;"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def insert_bill(self, data: Dict[str, Any]) -> int:
        """Create a new hospital invoice."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bills (
                    invoice_no, patient_id, appointment_id, consultation_fee,
                    service_charges, tax_percent, total_amount, payment_status,
                    bill_date, payment_method, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                data["invoice_no"], data["patient_id"], data.get("appointment_id"),
                float(data["consultation_fee"]), float(data["service_charges"]),
                float(data["tax_percent"]), float(data["total_amount"]),
                data.get("payment_status", "Pending"), data["bill_date"],
                data.get("payment_method", "Cash"), data.get("notes", "")
            ))
            conn.commit()
            return cursor.lastrowid

    def update_bill_payment_status(self, bill_id: int, status: str, payment_method: str = "Cash") -> bool:
        """Mark bill payment status as Paid or Pending."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE bills SET payment_status = ?, payment_method = ? WHERE id = ?;
            """, (status, payment_method, bill_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_next_invoice_no(self) -> str:
        """Generate sequential Invoice Number."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(id) FROM bills;")
            max_id = cursor.fetchone()[0] or 0
            year = datetime.date.today().year
            return f"INV-{year}-{1000 + max_id + 1}"

    # =========================================================================
    # AUDIT LOGS
    # =========================================================================
    def log_activity(self, user_id: Optional[int], action: str, details: str):
        """Record system security and operational activity into the audit log."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO activity_logs (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?);
            """, (user_id, action, details, timestamp))
            conn.commit()

    def get_recent_activity_logs(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Fetch the latest audit log entries with user attribution."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT al.*, u.full_name AS user_name, u.role
                FROM activity_logs al
                LEFT JOIN users u ON al.user_id = u.id
                ORDER BY al.id DESC
                LIMIT ?;
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # ADVANCED ANALYTICS QUERIES (FOR CANVAS CHARTS)
    # =========================================================================
    def get_monthly_patient_admissions(self) -> List[Tuple[str, int]]:
        """Get monthly patient counts for the current year."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT strftime('%m', registered_at) as month_num, COUNT(*) 
                FROM patients 
                GROUP BY month_num 
                ORDER BY month_num ASC;
            """)
            rows = cursor.fetchall()
            
            # Map month numbers to short names
            month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            month_counts = {m: 0 for m in month_names}
            for row in rows:
                if row[0]:
                    idx = int(row[0]) - 1
                    if 0 <= idx < 12:
                        month_counts[month_names[idx]] = row[1]
            return list(month_counts.items())

    def get_appointment_status_distribution(self) -> Dict[str, int]:
        """Get count breakdown of appointments grouped by status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) FROM appointments GROUP BY status;")
            rows = cursor.fetchall()
            dist = {"Scheduled": 0, "Completed": 0, "Cancelled": 0, "In Progress": 0}
            for status, count in rows:
                dist[status] = count
            return dist

    def get_doctor_workload_distribution(self) -> List[Tuple[str, int]]:
        """Get number of appointments per doctor specialization."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.specialization, COUNT(a.id)
                FROM doctors d
                LEFT JOIN appointments a ON d.id = a.doctor_id
                GROUP BY d.specialization
                ORDER BY COUNT(a.id) DESC
                LIMIT 5;
            """)
            return [(row[0], row[1]) for row in cursor.fetchall()]

    def get_revenue_timeline(self) -> List[Tuple[str, float]]:
        """Get past 6 chronological invoice records for revenue plotting."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT bill_date, SUM(total_amount)
                FROM bills
                WHERE payment_status = 'Paid'
                GROUP BY bill_date
                ORDER BY bill_date ASC
                LIMIT 8;
            """)
            rows = cursor.fetchall()
            if not rows:
                return [("Initial", 0.0)]
            return [(row[0], float(row[1])) for row in rows]


# Global database singleton
db = DatabaseManager()
