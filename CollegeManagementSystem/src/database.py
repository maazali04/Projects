import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path="data/college_core.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.initialize_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def update_student_status(self, student_id, new_status):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "UPDATE students SET status = ? WHERE enrollment_id = ?"
                cursor.execute(query, (new_status, student_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Database Error: {e}")
            return False

    def update_student_profile(self, data):
        """Updates Name, Roll No, Class, Shift, and Region for a student"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    UPDATE students 
                    SET name = ?, roll_no = ?, class_name = ?, shift = ?, region = ?
                    WHERE enrollment_id = ?
                """
                params = (
                    data.get("name"),
                    data.get("roll_no"),
                    data.get("class_name"),
                    data.get("shift"),
                    data.get("region"),
                    data.get("id"),
                )
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Database Error: {e}")
            return False

    def get_fee_records(self):
        """Fetches fee payments and maps them to UI keys"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT invoice_id, student_name, month, payment_status FROM fees"
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": r["invoice_id"],
                    "name": r["student_name"],
                    "month": r["month"],
                    "status": r["payment_status"],
                }
                for r in rows
            ]

    def get_examination_data(self):
        """Fetches all scheduled exams to display in the table."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, exam_name, class_name, exam_date, room_no FROM exams"
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching exams: {e}")
            return []

    def class_exists(self, class_name):
        """Checks if a class name actually exists in the classes table."""
        query = "SELECT 1 FROM classes WHERE class_name = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (class_name,))
            return cursor.fetchone() is not None

    def get_class_capacity_stats(self, class_name):
        """Returns a string like '5/20' by counting students in that class."""
        query_count = (
            "SELECT COUNT(*) FROM students WHERE class_name = ? AND status = 'Active'"
        )

        query_cap = "SELECT capacity FROM classes WHERE class_name = ?"

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query_count, (class_name,))
                current = cursor.fetchone()[0]

                cursor.execute(query_cap, (class_name,))
                result = cursor.fetchone()
                capacity = result[0] if result else "0"

            return f"{current}/{capacity}"
        except Exception as e:
            print(f"Error calculating stats: {e}")
            return "0/0"

    def get_all_students(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT enrollment_id, name, father_name, class_name, status FROM students"
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": r["enrollment_id"],
                    "name": r["name"],
                    "father_name": r["father_name"],
                    "class_name": r["class_name"],
                    "status": r["status"],
                }
                for r in rows
            ]

    def get_active_student_count(self, class_name):
        """Returns the integer count of active students in a specific class."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT COUNT(*) FROM students WHERE class_name = ? AND status = 'Active'"
                cursor.execute(query, (class_name,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Error counting students: {e}")
            return 0

    def delete_exam(self, exam_id):
        """Permanently removes an exam from the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Database Error during deletion: {e}")
            return False

    def get_all_class_names(self):
        """Returns a simple list of class names for dropdown menus."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT class_name FROM classes")
                return [row["class_name"] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching class names: {e}")
            return []

    def get_all_classes(self):
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT class_id, class_name, capacity, room, shift FROM classes"
                )
                rows = cursor.fetchall()

                classes_list = []
                for r in rows:
                    raw_db_capacity = str(r["capacity"]).split("/")[-1].strip()

                    current_count = self.get_active_student_count(r["class_name"])
                    stats = f"{current_count}/{raw_db_capacity}"

                    classes_list.append(
                        {
                            "id": r["class_id"],
                            "name": r["class_name"],
                            "capacity": stats,
                            "room": r["room"],
                            "shift": r["shift"],
                        }
                    )
                return classes_list
        except Exception as e:
            print(f"Database Error in get_all_classes: {e}")
            return []

    def save_attendance_batch(self, attendance_list):
        """
        attendance_list: List of dicts [{'student_id': 1, 'status': 'Present', 'date': '...'}, ...]
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = (
                    "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)"
                )
                data_to_insert = [
                    (item["student_id"], item["date"], item["status"])
                    for item in attendance_list
                ]
                cursor.executemany(query, data_to_insert)
                conn.commit()
                return True
        except Exception as e:
            print(f"Database Error during batch save: {e}")
            return False

    def get_dashboard_stats(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM students WHERE status='Active'")
            active_count = cursor.fetchone()[0]
            try:
                cursor.execute("SELECT COUNT(*) FROM fees")
                total_invoices = cursor.fetchone()[0]
            except Exception as e:
                total_invoices = 0
                print(f"Error counting invoices: {e}")

            return [
                {
                    "title": "Active Students",
                    "value": str(active_count),
                    "icon": "students.png",
                    "trend": "+0%",
                    "is_up": True,
                },
                {
                    "title": "Total Invoices",
                    "value": str(total_invoices),
                    "icon": "fee_records.png",
                    "trend": "Stable",
                    "is_up": True,
                },
            ]

    def get_student_attendance_history(self, student_id):
        """Fetches all past attendance records for a specific student"""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                query = """
                    SELECT date, status 
                    FROM attendance 
                    WHERE student_id = ? 
                    ORDER BY date DESC
                """
                cursor.execute(query, (student_id,))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching attendance history: {e}")
            return []

    def initialize_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS students (
                        enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        roll_no INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        father_name TEXT,
                        class_name TEXT NOT NULL,    
                        gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
                        status TEXT DEFAULT 'Active',
                        joining_date TEXT,
                        shift TEXT,
                        region TEXT,
                        UNIQUE(roll_no, class_name)
                    )
                """)
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS classes (
                        class_id TEXT PRIMARY KEY,
                        class_name TEXT NOT NULL,
                        capacity TEXT,
                        room TEXT,
                        shift TEXT
                    )
                """)

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER,
                        date TEXT, 
                        status TEXT CHECK(status IN ('Present', 'Absent', 'Leave', 'Late')),
                        class_name TEXT, 
                        -- FIX: Points to 'enrollment_id' to match Students table
                        FOREIGN KEY (student_id) REFERENCES students (enrollment_id) ON DELETE CASCADE,
                        UNIQUE(student_id, date) 
                    )
                """)

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS marks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER,
                        exam_id INTEGER,
                        subject_id INTEGER,
                        marks_obtained REAL,
                        total_marks REAL,
                        -- FIX: Points to 'enrollment_id'
                        FOREIGN KEY (student_id) REFERENCES students (enrollment_id) ON DELETE CASCADE,
                        FOREIGN KEY (exam_id) REFERENCES exams (id)
                    )
                """)

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS activity_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,         -- e.g., "New Student"
                        sub TEXT,                   -- e.g., "Maaz Ali registered for BSCS"
                        icon TEXT,                  -- e.g., "students.png"
                        color TEXT,                 -- e.g., "#E0F2FE" (background of icon circle)
                        time TEXT DEFAULT (DATETIME('now', 'localtime'))
                    )
                """)
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS fee_structure (class_name TEXT PRIMARY KEY, monthly_amount REAL DEFAULT 0.0)"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS fees (id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_id TEXT, student_name TEXT, class_name TEXT, month TEXT, payment_status TEXT)"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS exams (id INTEGER PRIMARY KEY AUTOINCREMENT, exam_name TEXT, class_name TEXT, exam_date TEXT, room_no TEXT)"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS activity_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, icon_name TEXT, title TEXT, description TEXT, time_ago TEXT, color_hex TEXT)"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS school_settings (key TEXT PRIMARY KEY, value TEXT)"
            )

            conn.commit()

    def check_roll_exists(self, roll, class_name, section=None):
        """Checks if a roll number is taken, handling NULL/Empty sections correctly."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if section and section.strip():
                cursor.execute(
                    """SELECT 1 FROM students WHERE roll_no=? AND class_name=? 
                               AND section=? AND status='Active'""",
                    (roll, class_name, section),
                )
            else:
                cursor.execute(
                    """SELECT 1 FROM students WHERE roll_no=? AND class_name=? 
                               AND (section IS NULL OR section='') AND status='Active'""",
                    (roll, class_name),
                )
            return cursor.fetchone() is not None

    def add_student(self, name, father_name, class_name, roll_no, gender):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            date_now = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                """
                INSERT INTO students (name, father_name, class_name, roll_no, gender, joining_date, status)
                VALUES (?, ?, ?, ?, ?, ?, 'Active')
            """,
                (name, father_name, class_name, roll_no, gender, date_now),
            )

            student_id = cursor.lastrowid
            current_month = datetime.now().strftime("%B %Y")
            invoice_id = f"INV-{student_id}{datetime.now().strftime('%S')}"

            cursor.execute(
                """
                INSERT INTO fees (invoice_id, student_name, month, payment_status)
                VALUES (?, ?, ?, 'Pending')
            """,
                (invoice_id, name, current_month),
            )

            conn.commit()
            return True, "Success"
        except Exception as e:
            conn.rollback()
            return False, f"DB Error: {str(e)}"
        finally:
            conn.close()

    def add_class(self, class_data):
        """
        Inserts a new class into the database.
        class_data: dict containing class_id, class_name, capacity, room, shift
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    INSERT INTO classes (class_id, class_name, capacity, room, shift)
                    VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(
                    query,
                    (
                        class_data.get("id"),
                        class_data.get("name"),
                        class_data.get("capacity"),
                        class_data.get("room"),
                        class_data.get("shift"),
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Database Error: {e}")
            return False

    def delete_class(self, class_id):
        """Permanently removes a class from the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "DELETE FROM classes WHERE class_id = ?"
                cursor.execute(query, (class_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Database Delete Error: {e}")
            return False

    def reindex_class(self, class_name, section=None):
        """Removes gaps by re-assigning roll numbers 1-N to Active students."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if section and section.strip():
                cursor.execute(
                    """SELECT enrollment_id FROM students WHERE class_name=? AND section=? 
                               AND status='Active' ORDER BY roll_no ASC""",
                    (class_name, section),
                )
            else:
                cursor.execute(
                    """SELECT enrollment_id FROM students WHERE class_name=? AND (section IS NULL OR section='') 
                               AND status='Active' ORDER BY roll_no ASC""",
                    (class_name,),
                )

            students = cursor.fetchall()
            for index, (enroll_id,) in enumerate(students, start=1):
                cursor.execute(
                    "UPDATE students SET roll_no = ? WHERE enrollment_id = ?",
                    (index, enroll_id),
                )
            conn.commit()

    def student_leaves(self, enroll_id):
        """Handles student exit and automatically triggers the 'Shift-Up' re-index."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT class_name, section FROM students WHERE enrollment_id = ?",
                (enroll_id,),
            )
            info = cursor.fetchone()
            if info:
                cursor.execute(
                    "UPDATE students SET status = 'Left', roll_no = 0 WHERE enrollment_id = ?",
                    (enroll_id,),
                )
                conn.commit()
                self.reindex_class(info[0], info[1])
                return True, "Student marked as Left and class re-indexed."
        return False, "Student not found."

    def student_fails(self, enroll_id):
        """Moves a failed student to the end of the class list."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT class_name, section FROM students WHERE enrollment_id = ?",
                (enroll_id,),
            )
            info = cursor.fetchone()
            if info:
                cursor.execute(
                    "UPDATE students SET roll_no = 9999 WHERE enrollment_id = ?",
                    (enroll_id,),
                )
                conn.commit()
                self.reindex_class(info[0], info[1])
                return True, "Student moved to last position."
        return False, "Error processing failure."

    def get_classes_with_enrollment(self):
        """Fetches classes and counts students currently in each."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.*, 
                    (SELECT COUNT(*) FROM students s WHERE s.class_name = c.name) as current_count
                    FROM classes c
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Database Error: {e}")
            return []

    def get_students_by_class(self, class_name):
        """Fetches all students enrolled in a specific class using the class name."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                query = (
                    "SELECT * FROM students WHERE class_name = ? AND status = 'Active'"
                )
                cursor.execute(query, (class_name,))

                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"DB Error fetching students for class {class_name}: {e}")
            return []

    def get_detailed_fee_status(self, student_name):
        """Calculates paid vs remaining for a specific student."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT class_name FROM students WHERE name = ?", (student_name,)
            )
            res = cursor.fetchone()
            class_name = res["class_name"] if res else None
            cursor.execute(
                "SELECT monthly_amount FROM fee_structure WHERE class_name = ?",
                (class_name,),
            )
            res = cursor.fetchone()
            total_required = res["monthly_amount"] if res else 0.0
            cursor.execute(
                "SELECT invoice_id, month, payment_status FROM fees WHERE student_name = ?",
                (student_name,),
            )
            history = [dict(row) for row in cursor.fetchall()]
            paid_count = len([r for r in history if r["payment_status"] == "Paid"])
            total_paid = paid_count * total_required

            return {
                "history": history,
                "total_paid": total_paid,
                "remaining": (total_required if paid_count == 0 else 0.0),
                "class_fee": total_required,
            }

    def get_student_fee_history(self, student_name):
        """Fetches all past invoices for a specific student."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT invoice_id as id, month, payment_status as status FROM fees WHERE student_name = ?"
                cursor.execute(query, (student_name,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching fee history: {e}")
            return []

    def record_payment(self, student_id, month_year, amount):
        """Updates the payment record. Supports partial payments."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            date_now = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                """
                UPDATE fee_payments SET amount_paid = amount_paid + ?, payment_date = ?
                WHERE student_id = ? AND month_year = ?
            """,
                (amount, date_now, student_id, month_year),
            )
            conn.commit()

    def get_student_balance(self, student_id):
        """Calculates total outstanding balance for a student."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT SUM(amount_due - amount_paid) FROM fee_payments WHERE student_id = ?",
                (student_id,),
            )
            balance = cursor.fetchone()[0]
            return balance if balance else 0.0

    def collect_student_fee(self, invoice_id, amount_paid):
        """Marks an invoice as Paid and logs the amount."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "UPDATE fees SET payment_status = 'Paid' WHERE invoice_id = ?"
                cursor.execute(query, (invoice_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Collection Error: {e}")
            return False

    def add_new_exam(self, exam_data):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    INSERT INTO exams (exam_name, class_name, exam_date, room_no)
                    VALUES (?, ?, ?, ?)
                """
                cursor.execute(
                    query,
                    (
                        exam_data["exam_name"],
                        exam_data["class_name"],
                        exam_data["exam_date"],
                        exam_data.get("room_no", "N/A"),
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Database Error: {e}")
            return False

    def add_marks(self, student_id, exam_id, subject_id, obtained, total):
        """Records student marks. Updates if record already exists."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO marks (student_id, exam_id, subject_id, marks_obtained, total_marks)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET marks_obtained=excluded.marks_obtained
            """,
                (student_id, exam_id, subject_id, obtained, total),
            )
            conn.commit()

    def get_all_settings(self):
        """Fetches all key-value pairs from school_settings table"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM school_settings")
                return {row[0]: row[1] for row in cursor.fetchall()}
        except Exception as e:
            print(f"Error fetching settings: {e}")
            return {}

    def update_settings(self, settings_dict):
        """Saves or updates multiple settings at once"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for key, value in settings_dict.items():
                    cursor.execute(
                        "INSERT OR REPLACE INTO school_settings (key, value) VALUES (?, ?)",
                        (key, value),
                    )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating settings: {e}")
            return False

    def log_activity(self, action, details):
        """
        Records an event into the activity_log table.
        Example: log_activity("Registration", "Maaz Ali was added to BSCS")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO activity_log (action, details, timestamp)
                VALUES (?, ?, DATETIME('now', 'localtime'))
            """,
                (action, details),
            )
            conn.commit()

    def get_recent_activities(self, limit=5):
        """Fetches activity logs and formats them for the ComponentFactory"""
        query = """
            SELECT title, sub, icon, color, time 
            FROM activity_log 
            ORDER BY id DESC 
            LIMIT ?
        """
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Database Error: {e}")
            return []

    def add_activity(self, title, sub, icon, color="#F1F5F9"):
        """
        Physically writes a new row to the activity_log table.
        """
        query = """
            INSERT INTO activity_log (title, sub, icon, color, time)
            VALUES (?, ?, ?, ?, DATETIME('now', 'localtime'))
        """
        try:
            with self._get_connection() as conn:
                conn.execute(query, (title, sub, icon, color))
                conn.commit()
                print(f"Successfully logged activity: {title}")
        except Exception as e:
            print(f"Logging Error: {e}")

    def log_event(self, category, details):
        """
        A universal logger to be called after any successful operation.
        Categories: 'Student', 'Fee', 'Exam', 'System'
        """
        colors = {
            "Student": "#DCFCE7",
            "Fee": "#F0F9FF",
            "Exam": "#FFFBEB",
            "System": "#F1F5F9",
        }
        icons = {
            "Student": "students.png",
            "Fee": "fee_records.png",
            "Exam": "examination.png",
            "System": "dashboard.png",
        }

        self.add_activity(
            title=category,
            sub=details,
            icon=icons.get(category, "dashboard.png"),
            color=colors.get(category, "#F1F5F9"),
        )
