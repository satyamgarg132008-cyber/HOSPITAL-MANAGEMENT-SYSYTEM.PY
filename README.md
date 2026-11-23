# MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
> **Smart Healthcare. Intelligent Management.**  
> *A University Python Capstone Project engineered with a Tony Stark J.A.R.V.I.S.-inspired Futuristic Desktop Interface.*

---

## 1. Project Overview

**MEDNOVA AI** is a state-of-the-art, fully offline Windows desktop Hospital Management System (HMS) developed with **Python 3.11+**, **Tkinter / ttk**, and **SQLite3**. 

Designed to look like an advanced sci-fi hospital command control center (inspired by Tony Stark's J.A.R.V.I.S. and Stark Tower medical bay telemetry), the application provides comprehensive hospital workflow automation:
- **Biometric & Credential Access Gateway** with PBKDF2-HMAC-SHA256 cryptographic password hashing and role-based access control (Admin, Doctor, Receptionist).
- **Holographic Command Dashboard** with real-time SQLite metrics and an animated multi-ring Canvas Arc Reactor AI Core.
- **Patient Census Registry** with unique automated UID generation (`MED-P-YYYY-XXXX`), demographic records, and validation.
- **Physician & Surgical Staff Roster** with departmental scheduling, room allocations, consultation fee management, and instant duty status toggling.
- **Intelligent Appointment Scheduler** featuring **real-time doctor schedule collision/conflict detection** to prevent double-booking.
- **Financial Billing Engine** utilizing Python's `Decimal` module for zero-roundoff financial precision, generating itemized printable/exportable ASCII holographic receipts.
- **Electronic Health Records (EHR) Medical Archive** providing chronological clinical encounter logs, diagnoses, treatments, and prescriptions.
- **Native Tkinter Canvas Visual Analytics** with multi-dimensional hospital census telemetry (monthly admissions bar charts, appointment status doughnut charts, financial line plots, and department workload charts).
- **Offline J.A.R.V.I.S. Voice Engine** powered by `pyttsx3` with background daemon threading for non-blocking speech announcements.

---

## 2. System Architecture & Folder Structure

```
MEDNOVA_AI/
│
├── main.py                     # Application entry point & master bootstrapper
├── config.py                   # Global constants, holographic palette, fonts, permissions
├── database.py                 # SQLite3 schema, foreign keys, transactions & demo seed data
├── security.py                 # PBKDF2 password hashing & active session management
├── login.py                    # Futuristic Stark-themed authentication gateway
├── gui.py                      # Master shell, topbar, digital clock, animated sidebar
├── dashboard.py                # Executive KPI metrics, animated Canvas AI Core, live feeds
├── patient_management.py       # Patient registration, search, CRUD, and validations
├── doctor_management.py        # Physician roster, department scheduling, duty toggle
├── appointment_management.py   # Visit scheduler with real-time conflict detection
├── medical_history.py          # Chronological clinical dossiers & prescription archive
├── billing.py                  # Financial ledger, Decimal calculations & ASCII invoices
├── analytics.py                # 100% native Tkinter Canvas charts & visual telemetry
├── voice_engine.py             # Non-blocking pyttsx3 voice synthesizer with worker queue
├── utils.py                    # UI widget decorators, validators, currency & invoice tools
├── requirements.txt            # Python package dependencies
├── README.md                   # Complete documentation, setup guide, test cases & viva Q&A
├── invoices/                   # Auto-created directory for generated .txt receipts
└── exports/                    # Auto-created directory for exported CSV spreadsheets
```

---

## 3. Installation & Setup Guide

### System Prerequisites
- **Operating System:** Windows 10 or Windows 11 (64-bit)
- **Python Version:** Python 3.11, 3.12, or 3.13+
- **Database:** SQLite3 (built into Python standard library)
- **GUI Engine:** Tkinter & ttk (included with standard Windows Python installations)

### Step 1: Open VS Code in the Project Folder
1. Launch **Visual Studio Code**.
2. Go to **File -> Open Folder...** and select the `MEDNOVA_AI` folder:
   ```
   C:\Users\ASHISH SHARMA\.gemini\antigravity\scratch\MEDNOVA_AI
   ```

### Step 2: Open Terminal in VS Code
Open an integrated PowerShell terminal in VS Code (`Ctrl + ` `~` or **Terminal -> New Terminal**).

### Step 3: Install Required Dependencies
Run the following command to install the offline speech synthesizer:
```bash
pip install -r requirements.txt
```
*(Note: If `pyttsx3` is already installed, this will complete instantly. The entire database, GUI, and cryptographic engines use Python's built-in standard library).*

---

## 4. How to Run the Application

Execute the following command in your terminal:
```bash
python main.py
```
*(Or if using the specific Python launcher on your Windows system):*
```powershell
& 'C:\Users\ASHISH SHARMA\AppData\Local\Programs\Python\Python313\python.exe' main.py
```

---

## 5. Demonstration Accounts & Login Credentials

MEDNOVA AI is pre-configured with realistic fictional demonstration accounts for university presentation. On the login screen, click any of the **`[ADMIN]`**, **`[DOCTOR]`**, or **`[RECEPTION]`** buttons to auto-fill credentials with one click!

| Role | Username | Password | Full Name / Title | Clearance & Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Chief Director Tony Stark | Unrestricted access to all 7 command modules |
| **Doctor** | `dr_tony` | `stark123` | Dr. Tony Stark, MD, PhD | Dashboard, Patients, Appointments, Medical History, Analytics |
| **Doctor** | `dr_banner` | `banner123` | Dr. Bruce Banner, MD, PhD | Dashboard, Patients, Appointments, Medical History, Analytics |
| **Receptionist**| `recep_pepper` | `pepper123` | Ms. Pepper Potts | Dashboard, Patients, Doctors, Appointments, Billing |

---

## 6. Comprehensive Test Cases for University Demonstration

### Test Case 1: Cryptographic Authentication & Role Clearance
- **Module:** `login.py` / `security.py`
- **Objective:** Verify PBKDF2 password hashing verification and role-based module filtering.
- **Input:** Username: `recep_pepper`, Password: `pepper123`.
- **Steps:**
  1. Click the `[RECEPTION]` quick preset or enter credentials manually.
  2. Click **"INITIALIZE COMMAND ACCESS"**.
- **Expected Result:**
  - J.A.R.V.I.S. voice announces: *"Welcome to Med Nova AI Command Center, Ms. Pepper Potts. Security authorization level: Receptionist..."*
  - Topbar displays logged-in user badge with Receptionist clearance.
  - Sidebar shows accessible modules (Dashboard, Patients, Doctors, Appointments, Billing), automatically hiding restricted modules (Medical Archive, Visual Analytics).
- **Status:** **PASS**

---

### Test Case 2: Patient Registration with Unique ID & Auto-Age Calculation
- **Module:** `patient_management.py`
- **Objective:** Enroll a new patient, test DOB-to-age calculator, and verify database persistence.
- **Input:**
  - Name: `Wong Kam-Chi`
  - DOB: `1985-06-15`
  - Gender: `Male`, Blood Group: `O+`
  - Phone: `+1-555-0999`, Emergency Contact: `Stephen Strange (+1-555-0103)`
- **Steps:**
  1. Navigate to **Patient Registry**.
  2. Click **"➕ NEW PATIENT"**.
  3. Enter DOB `1985-06-15` — observe the Age field dynamically calculate `41`.
  4. Fill remaining fields and click **"COMMIT TO DATABASE"**.
- **Expected Result:**
  - Database assigns sequential UID `MED-P-2026-0007`.
  - Voice engine announces: *"Patient registration confirmed for Wong Kam-Chi. Record identifier MED-P-2026-0007."*
  - Table instantly refreshes displaying the new record.
- **Status:** **PASS**

---

### Test Case 3: Intelligent Appointment Booking Conflict Detection
- **Module:** `appointment_management.py` / `database.py`
- **Objective:** Validate real-time schedule conflict engine preventing physician double-booking.
- **Input:**
  - Doctor: `Dr. Tony Stark, MD, PhD`
  - Date: Select **Today's Date**
  - Time Slot: `09:30 AM` (Existing booking slot from demo dataset)
- **Steps:**
  1. Navigate to **Appointments**.
  2. Click **"➕ BOOK VISIT"**.
  3. Select any patient, select `Dr. Tony Stark`, date as today, and slot as `09:30 AM`.
  4. Click **"CONFIRM & DISPATCH BOOKING"**.
- **Expected Result:**
  - System intercepts booking and displays an error alert:  
    `SCHEDULE COLLISION: Dr. Tony Stark, MD, PhD is ALREADY BOOKED for a consultation on [Date] at 09:30 AM.`
  - Database rejects double booking; appointment count remains accurate.
- **Status:** **PASS**

---

### Test Case 4: Precise Financial Billing with Python `Decimal`
- **Module:** `billing.py` / `utils.py`
- **Objective:** Verify zero-roundoff arithmetic and printable holographic invoice generation.
- **Input:**
  - Consultation Fee: `250.00`
  - Additional Service Charges: `125.50`
  - Tax Rate: `5.0%`
- **Steps:**
  1. Navigate to **Billing & Invoices**.
  2. Click **"➕ NEW INVOICE"**.
  3. Enter Consultation: `250.00`, Services: `125.50`, Tax: `5.0`.
  4. Observe the live calculated total:  
     $$\text{Subtotal} = 250.00 + 125.50 = 375.50$$  
     $$\text{Tax (5\%)} = 375.50 \times 0.05 = 18.775 \rightarrow 18.78$$  
     $$\text{Net Total} = 375.50 + 18.78 = 394.28$$
  5. Click **"ISSUE INVOICE"**, then select the invoice and click **"PRINT / VIEW"**.
- **Expected Result:**
  - Holographic invoice modal renders formatted ASCII receipt with patient dossier and crypto-signature stamp.
  - Clicking **"SAVE TO DISK"** exports a clean `.txt` receipt into the `invoices/` folder.
- **Status:** **PASS**

---

### Test Case 5: Real-Time Tkinter Canvas Visual Analytics Redraw
- **Module:** `analytics.py`
- **Objective:** Verify native Tkinter Canvas charts draw without external libraries and update with database changes.
- **Steps:**
  1. Navigate to **Visual Analytics**.
  2. Inspect the 4 visual quadrants:
     - Quad 1: Monthly Patient Admissions (Cyan bar chart with value labels).
     - Quad 2: Appointments Breakdown (Multi-color doughnut chart with inner cutout).
     - Quad 3: Revenue Ledger Trajectory (Cobalt line plot with green glowing data nodes).
     - Quad 4: Departmental Caseload (Horizontal department workload bars).
  3. Click **"↻ RECALCULATE TELEMETRY"**.
- **Expected Result:**
  - All 4 canvases execute mathematical coordinate transformations and re-plot instantly at 60 FPS without UI freezing.
- **Status:** **PASS**

---

## 7. University Viva Questions & Model Answers

### Q1: Why did you choose Tkinter and SQLite for this project?
> **Answer:** Tkinter is the standard Python GUI library across all operating systems. It runs natively with zero external graphic dependencies, providing superior responsiveness when building desktop applications. SQLite3 is an ACID-compliant, serverless, self-contained relational database embedded directly inside Python. It enables full relational integrity with zero network latency, making it ideal for robust desktop deployments.

### Q2: How did you implement the Tony Stark / J.A.R.V.I.S. futuristic theme in Tkinter?
> **Answer:** We implemented a custom design system based on deep navy space backgrounds (`#050814`, `#0A1128`), holographic card containers, and glowing neon accents (Arc Reactor Cyan `#00F0FF`, Cobalt Blue `#0080FF`, and Emerald `#00FF88`). We created custom subclasses like `GlowingButton` with `<Enter>` and `<Leave>` hover animations, custom ttk `Treeview` styles, and designed an animated circular AI Core rendered dynamically using trigonometry on a native Tkinter `Canvas` with an `after()` event loop timer.

### Q3: How is password security managed in the application?
> **Answer:** Passwords are never stored in plain text. We utilize the cryptographic **PBKDF2-HMAC-SHA256** key derivation algorithm with **100,000 hashing iterations** and a unique cryptographically secure 16-byte random salt generated via `secrets.token_hex(16)`. During authentication, we compare calculated hashes using `secrets.compare_digest()` to eliminate side-channel timing attacks.

### Q4: How does the Appointment Conflict Detection algorithm work?
> **Answer:** When booking an appointment, the system queries the SQLite database using a parameterized `SELECT COUNT(*)` query filtering for the selected `doctor_id`, `appointment_date`, `appointment_time`, and verifying `status != 'Cancelled'`. If a matching record is returned, the booking is intercepted and the user receives a warning alert, ensuring doctors are never scheduled for two concurrent consultations.

### Q5: Why did you use Python's `Decimal` instead of standard `float` for billing calculations?
> **Answer:** Standard IEEE 754 floating-point numbers are binary approximations and introduce round-off errors in financial math (e.g., `0.1 + 0.2 = 0.30000000000000004`). In a clinical billing system, financial discrepancies are unacceptable. Python's `decimal.Decimal` with `ROUND_HALF_UP` guarantees exact fixed-point base-10 arithmetic for all consultation charges, hospital surcharges, and tax calculations.

### Q6: How does the Voice Assistant operate without freezing the Tkinter GUI?
> **Answer:** Tkinter operates on a single-threaded event loop (`mainloop()`). If a synchronous Text-to-Speech (TTS) call like `engine.runAndWait()` runs on the main thread, the entire GUI locks until speech finishes. To solve this, we encapsulated `pyttsx3` inside a decoupled **daemon thread** coupled with a thread-safe `queue.Queue()`. Speech requests are pushed to the queue instantaneously, while the background worker processes audio independently, keeping the GUI smooth.

### Q7: What are the primary database relationships implemented in your schema?
> **Answer:** The schema incorporates foreign keys with relational constraints:
> - `appointments` references `patients(id)` and `doctors(id)` with `ON DELETE CASCADE`.
> - `medical_history` references `patients(id)` with `CASCADE` and `doctors(id)` with `ON DELETE SET NULL`.
> - `bills` references `patients(id)` with `CASCADE` and optional `appointments(id)` with `SET NULL`.
> - `activity_logs` references `users(id)` for audit logging. Foreign keys are enforced via `PRAGMA foreign_keys = ON;`.

### Q8: How is Role-Based Access Control (RBAC) enforced?
> **Answer:** A singleton `UserSession` class holds active authenticated user properties. Navigation permissions are mapped in `config.ROLE_PERMISSIONS`. Upon login, the sidebar dynamically filters navigation buttons based on the user's role. If an unauthorized attempt is made, `navigate_to()` blocks the action and logs a security notice in the audit log.

---

## 8. Troubleshooting & FAQ

- **Issue:** Tkinter window says "No module named pyttsx3" or voice doesn't speak.
  - **Fix:** MedNova AI includes automatic graceful fallback: the app will run smoothly even without audio. To enable voice, run:
    ```bash
    pip install pyttsx3
    ```
- **Issue:** Window appears too small or zoomed in on high-DPI displays.
  - **Fix:** MedNova AI is built with responsive window resizing and minimum bounds of `1280x800`. Maximize the window or resize using standard window controls.
- **Issue:** How to reset database back to factory demo state?
  - **Fix:** Delete the `mednova.db` file in the `MEDNOVA_AI/` folder. Rerun `python main.py`; the system will automatically re-create the schema and re-seed all Stark demo records.

---
*Developed for University Capstone Project Demonstration • MEDNOVA AI SYSTEMS 2026*
