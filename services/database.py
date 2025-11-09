# -*- coding: utf-8 -*-
"""
שכבת בסיס הנתונים - Database Layer
"""

import sqlite3
from datetime import datetime
import os
import sys
import shutil


def get_application_path():
    """קבלת נתיב התיקייה של התוכנה (עובד גם עם EXE)"""
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
        # אם בתיקייה של services, עלה לתיקייה הראשית
        while os.path.basename(application_path) in ['services', 'models', 'ui', 'utils']:
            application_path = os.path.dirname(application_path)
    return application_path


def get_data_path(filename):
    """קבלת נתיב מלא לקובץ נתונים"""
    return os.path.join(get_application_path(), filename)


def create_backup(db_path):
    """יצירת גיבוי אוטומטי של מסד הנתונים"""
    if not os.path.exists(db_path):
        return False

    backup_dir = os.path.join(get_application_path(), "backups")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_name)

    try:
        shutil.copy2(db_path, backup_path)
        # שמירת רק 10 גיבויים אחרונים
        backups = sorted([f for f in os.listdir(backup_dir) if f.startswith("backup_")])
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                os.remove(os.path.join(backup_dir, old_backup))
        return True
    except Exception as e:
        print(f"שגיאה ביצירת גיבוי: {e}")
        return False


class YeshivaDatabase:
    """מחלקה לניהול מסד הנתונים"""

    def __init__(self, db_name="yeshiva_new.db"):
        self.db_name = get_data_path(db_name)
        self.init_database()

    def init_database(self):
        """יצירת טבלאות במסד הנתונים"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # טבלת תלמידים
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                id_number TEXT,
                birth_date_hebrew TEXT,
                address TEXT,
                city TEXT,
                father_name TEXT,
                father_id_number TEXT,
                mother_name TEXT,
                mother_id_number TEXT,
                father_phone TEXT,
                mother_phone TEXT,
                home_phone TEXT,
                entry_date_hebrew TEXT,
                current_grade TEXT,
                initial_grade TEXT,
                status TEXT DEFAULT 'פעיל',
                framework_type TEXT DEFAULT 'רגיל',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_grade_update TEXT
            )
        ''')

        # הוספת עמודות חדשות אם הטבלה כבר קיימת
        try:
            cursor.execute('ALTER TABLE students ADD COLUMN city TEXT')
        except sqlite3.OperationalError:
            pass  # העמודה כבר קיימת

        try:
            cursor.execute('ALTER TABLE students ADD COLUMN father_id_number TEXT')
        except sqlite3.OperationalError:
            pass  # העמודה כבר קיימת

        try:
            cursor.execute('ALTER TABLE students ADD COLUMN mother_id_number TEXT')
        except sqlite3.OperationalError:
            pass  # העמודה כבר קיימת

        # טבלת נוכחות שחרית (ישנה - לשמירה לאחור)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shacharit_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date_hebrew TEXT,
                date_gregorian TEXT,
                attended INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                UNIQUE(student_id, date_hebrew)
            )
        ''')

        # טבלת הגדרת סשנים (תפילות וסדרי לימוד)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                display_order INTEGER NOT NULL,
                icon TEXT,
                active_days TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # טבלת נוכחות חדשה - תומכת בתפילות וסדרי לימוד
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date_hebrew TEXT,
                date_gregorian TEXT,
                session_type TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'תפילה',
                status TEXT NOT NULL DEFAULT 'חסר',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                UNIQUE(student_id, date_gregorian, session_type)
            )
        ''')

        # Migration: טיפול בעמודות ישנות אם הטבלה כבר קיימת עם המבנה הישן
        try:
            # בדיקה אם יש עמודה ישנה prayer_type (לפני שינוי)
            cursor.execute("PRAGMA table_info(attendance)")
            columns = {col[1]: col[2] for col in cursor.fetchall()}

            # אם קיימת עמודה prayer_type, צריך להעביר את הנתונים לטבלה חדשה
            if 'prayer_type' in columns and 'session_type' not in columns:
                print("מזהה מבנה ישן - מבצע migration...")

                # גיבוי הנתונים
                cursor.execute('''
                    CREATE TEMPORARY TABLE attendance_backup AS
                    SELECT * FROM attendance
                ''')

                # מחיקת הטבלה הישנה
                cursor.execute('DROP TABLE attendance')

                # יצירת הטבלה החדשה
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER,
                        date_hebrew TEXT,
                        date_gregorian TEXT,
                        session_type TEXT NOT NULL,
                        category TEXT NOT NULL DEFAULT 'תפילה',
                        status TEXT NOT NULL DEFAULT 'חסר',
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                        UNIQUE(student_id, date_gregorian, session_type)
                    )
                ''')

                # העברת הנתונים עם המרה: attended (0/1) → status (חסר/נוכח)
                cursor.execute('''
                    INSERT OR IGNORE INTO attendance
                    (student_id, date_hebrew, date_gregorian, session_type, category, status, notes, created_at)
                    SELECT
                        student_id,
                        date_hebrew,
                        date_gregorian,
                        prayer_type,
                        'תפילה',
                        CASE WHEN attended = 1 THEN 'נוכח' ELSE 'חסר' END,
                        notes,
                        created_at
                    FROM attendance_backup
                ''')

                cursor.execute('DROP TABLE attendance_backup')
                print("Migration הושלם בהצלחה!")
        except Exception as e:
            print(f"הערה: {e}")
            pass

        # העתקת נתונים מהטבלה הישנה shacharit_attendance אם יש
        cursor.execute('''
            INSERT OR IGNORE INTO attendance (student_id, date_hebrew, date_gregorian, session_type, category, status, notes, created_at)
            SELECT
                student_id,
                date_hebrew,
                date_gregorian,
                'שחרית',
                'תפילה',
                CASE WHEN attended = 1 THEN 'נוכח' ELSE 'חסר' END,
                notes,
                created_at
            FROM shacharit_attendance
        ''')

        # אכלוס הגדרות הסשנים (תפילות + סדרי לימוד)
        import json

        sessions_to_add = [
            # תפילות (3)
            ('שחרית', 'תפילה', 1, '🌅', json.dumps([0,1,2,3,4,5,6])),  # כל יום
            ('מנחה', 'תפילה', 2, '☀️', json.dumps([0,1,2,3,4])),  # ראשון-חמישי
            ('מעריב', 'תפילה', 3, '🌙', json.dumps([0,1,2,3,4])),  # ראשון-חמישי

            # סדרי לימוד (9)
            ('שיעור בקיאות', 'לימוד', 4, '📖', json.dumps([0,1,2,3,4,5,6])),  # כל יום
            ('סדר א\' - חזרה עיון', 'לימוד', 5, '📝', json.dumps([0,1,2,3,4])),  # ראשון-חמישי
            ('שיעור עיון', 'לימוד', 6, '📚', json.dumps([0,1,2,3,4,5,6])),  # כל יום
            ('שיעור עיון 2', 'לימוד', 7, '📘', json.dumps([0,1,2,3,4])),  # ראשון-חמישי
            ('שיעור גמרא רש"י', 'לימוד', 8, '📜', json.dumps([0,1,2,3,4])),  # ראשון-חמישי
            ('שיעור חומש רש"י', 'לימוד', 9, '📕', json.dumps([0,1,2,5])),  # ראשון-שלישי + שישי
            ('הלכה', 'לימוד', 10, '⚖️', json.dumps([3,4])),  # רביעי-חמישי
            ('סדר ב\' - חזרה בקיאות', 'לימוד', 11, '🔄', json.dumps([0,1,2,3,4])),  # ראשון-חמישי
            ('סדר ג\' - הכנה עיון', 'לימוד', 12, '📋', json.dumps([0,1,2,3,4])),  # ראשון-חמישי
        ]

        for session_name, category, display_order, icon, active_days in sessions_to_add:
            cursor.execute('''
                INSERT OR IGNORE INTO session_definitions
                (session_name, category, display_order, icon, active_days)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_name, category, display_order, icon, active_days))

        # ===== טבלאות מבחנים =====

        # טבלת מבחנים
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                syllabus_text TEXT,
                grade TEXT,
                total_points INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                academic_year TEXT,
                semester TEXT,
                status TEXT DEFAULT 'draft'
            )
        ''')

        # טבלת שאלות מבחן
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exam_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER,
                question_number INTEGER,
                question_text TEXT NOT NULL,
                points INTEGER DEFAULT 10,
                question_type TEXT DEFAULT 'essay',
                correct_answer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
                UNIQUE(exam_id, question_number)
            )
        ''')

        # טבלת גרסאות מבחן
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exam_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER,
                version_code TEXT NOT NULL,
                questions_order TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
                UNIQUE(exam_id, version_code)
            )
        ''')

        # טבלת הקצאת מבחנים לתלמידים
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                exam_id INTEGER,
                version_id INTEGER,
                scheduled_date DATE,
                actual_date DATE,
                status TEXT DEFAULT 'scheduled',
                postponement_reason TEXT,
                postponed_to_date DATE,
                pdf_generated_path TEXT,
                qr_code_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
                FOREIGN KEY (version_id) REFERENCES exam_versions(id),
                UNIQUE(student_id, exam_id)
            )
        ''')

        # טבלת ציונים
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exam_grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_exam_id INTEGER,
                total_score INTEGER,
                grade_percent REAL,
                graded_by TEXT,
                graded_at TIMESTAMP,
                grading_method TEXT DEFAULT 'manual',
                ocr_confidence REAL,
                needs_review BOOLEAN DEFAULT 0,
                scanned_pdf_path TEXT,
                notes TEXT,
                FOREIGN KEY (student_exam_id) REFERENCES student_exams(id) ON DELETE CASCADE
            )
        ''')

        # טבלת ציונים ברמת שאלה
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS question_grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grade_id INTEGER,
                question_id INTEGER,
                points_earned INTEGER,
                points_possible INTEGER,
                feedback TEXT,
                FOREIGN KEY (grade_id) REFERENCES exam_grades(id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES exam_questions(id)
            )
        ''')

        # טבלת הספקים (syllabi)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subject_syllabi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grade TEXT NOT NULL,
                subject TEXT NOT NULL,
                masechet TEXT,
                daf_start TEXT,
                daf_end TEXT,
                chumash TEXT,
                chapter_start TEXT,
                chapter_end TEXT,
                halacha_section TEXT,
                siman_start TEXT,
                siman_end TEXT,
                target_exam_date DATE,
                academic_year TEXT,
                semester TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(grade, subject, academic_year, semester)
            )
        ''')

        # אינדקסים לביצועים
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_exams_student ON student_exams(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_exams_exam ON student_exams(exam_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_exams_date ON student_exams(scheduled_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_exam_grades_student_exam ON exam_grades(student_exam_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_exam_questions_exam ON exam_questions(exam_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_syllabi_grade ON subject_syllabi(grade, subject)')

        conn.commit()
        conn.close()

    def add_student(self, student_data):
        """הוספת תלמיד חדש"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO students (
                first_name, last_name, id_number,
                birth_date_hebrew, address, city,
                father_name, father_id_number, mother_name, mother_id_number,
                father_phone, mother_phone, home_phone,
                entry_date_hebrew,
                current_grade, initial_grade, status, framework_type, notes,
                last_grade_update
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_data.get('first_name', ''), student_data.get('last_name', ''), student_data.get('id_number', ''),
            student_data.get('birth_date_hebrew', ''), student_data.get('address', ''), student_data.get('city', ''),
            student_data.get('father_name', ''), student_data.get('father_id_number', ''),
            student_data.get('mother_name', ''), student_data.get('mother_id_number', ''),
            student_data.get('father_phone', ''), student_data.get('mother_phone', ''), student_data.get('home_phone', ''),
            student_data.get('entry_date_hebrew', ''),
            student_data.get('current_grade', ''), student_data.get('current_grade', ''),
            student_data.get('status', 'פעיל'), student_data.get('framework_type', 'רגיל'), student_data.get('notes', ''),
            datetime.now().strftime('%Y-%m-%d')
        ))

        student_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return student_id

    def get_all_students(self, include_inactive=False):
        """קבלת רשימת כל התלמידים"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        if include_inactive:
            cursor.execute('''SELECT id, first_name, last_name, id_number, birth_date_hebrew, address, city,
                            father_name, father_id_number, mother_name, mother_id_number,
                            father_phone, mother_phone, home_phone,
                            entry_date_hebrew, current_grade, initial_grade, status, framework_type,
                            notes, created_at, last_grade_update FROM students ORDER BY last_name, first_name''')
        else:
            cursor.execute('''SELECT id, first_name, last_name, id_number, birth_date_hebrew, address, city,
                            father_name, father_id_number, mother_name, mother_id_number,
                            father_phone, mother_phone, home_phone,
                            entry_date_hebrew, current_grade, initial_grade, status, framework_type,
                            notes, created_at, last_grade_update FROM students WHERE status = "פעיל" ORDER BY last_name, first_name''')

        students = cursor.fetchall()
        conn.close()
        return students

    def get_student(self, student_id):
        """קבלת פרטי תלמיד"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # מאפשר גישה לעמודות לפי שם
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_student(self, student_id, student_data):
        """עדכון פרטי תלמיד"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE students
            SET first_name=?, last_name=?, id_number=?,
                birth_date_hebrew=?, address=?,
                father_name=?, mother_name=?,
                father_phone=?, mother_phone=?, home_phone=?,
                entry_date_hebrew=?,
                current_grade=?, status=?, framework_type=?, notes=?
            WHERE id=?
        ''', (
            student_data['first_name'], student_data['last_name'], student_data['id_number'],
            student_data['birth_date_hebrew'], student_data['address'],
            student_data['father_name'], student_data['mother_name'],
            student_data['father_phone'], student_data['mother_phone'], student_data['home_phone'],
            student_data['entry_date_hebrew'],
            student_data['current_grade'], student_data['status'],
            student_data['framework_type'], student_data['notes'],
            student_id
        ))

        conn.commit()
        conn.close()

    def delete_student(self, student_id):
        """מחיקת תלמיד"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.commit()
        conn.close()

    def delete_all_students(self):
        """מחיקת כל התלמידים"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM students')
        conn.commit()
        conn.close()

    def save_attendance(self, student_id, date_hebrew, date_gregorian, status, session_type='שחרית', category='תפילה'):
        """שמירת נוכחות - תומך בתפילות וסדרי לימוד

        Args:
            student_id: מזהה תלמיד
            date_hebrew: תאריך עברי
            date_gregorian: תאריך גרגוריאני
            status: 'נוכח', 'חסר', או 'איחור'
            session_type: שם הסשן (תפילה או סדר לימוד)
            category: 'תפילה' או 'לימוד'
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # שמירה בטבלה החדשה
        cursor.execute('''
            INSERT OR REPLACE INTO attendance
            (student_id, date_hebrew, date_gregorian, session_type, category, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (student_id, date_hebrew, date_gregorian, session_type, category, status))

        # שמירה גם בטבלה הישנה אם זה שחרית (לשמירה לאחור)
        if session_type == 'שחרית':
            attended = 1 if status == 'נוכח' else 0
            cursor.execute('''
                INSERT OR REPLACE INTO shacharit_attendance
                (student_id, date_hebrew, date_gregorian, attended)
                VALUES (?, ?, ?, ?)
            ''', (student_id, date_hebrew, date_gregorian, attended))

        conn.commit()
        conn.close()

    def get_attendance(self, student_id, date_hebrew, session_type='שחרית'):
        """קבלת נוכחות לתאריך וסשן מסוים

        Returns:
            'נוכח', 'חסר', 'איחור', או None אם לא קיים
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT status FROM attendance
            WHERE student_id = ? AND date_hebrew = ? AND session_type = ?
        ''', (student_id, date_hebrew, session_type))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_week_attendance(self, start_date_hebrew, end_date_hebrew):
        """קבלת נוכחות לשבוע"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT student_id, date_hebrew, attended
            FROM shacharit_attendance
            WHERE date_hebrew BETWEEN ? AND ?
        ''', (start_date_hebrew, end_date_hebrew))
        results = cursor.fetchall()
        conn.close()

        attendance_dict = {}
        for student_id, date_heb, attended in results:
            if student_id not in attendance_dict:
                attendance_dict[student_id] = {}
            attendance_dict[student_id][date_heb] = attended

        return attendance_dict

    def get_student_attendance_stats(self, student_id):
        """קבלת סטטיסטיקות נוכחות של תלמיד"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM shacharit_attendance
            WHERE student_id = ? AND attended = 1
        ''', (student_id,))
        total_present = cursor.fetchone()[0]

        cursor.execute('''
            SELECT COUNT(*) FROM shacharit_attendance
            WHERE student_id = ? AND attended = 0
        ''', (student_id,))
        total_absent = cursor.fetchone()[0]

        conn.close()

        total_days = total_present + total_absent
        percentage = (total_present / total_days * 100) if total_days > 0 else 0

        return {
            'total_present': total_present,
            'total_absent': total_absent,
            'total_days': total_days,
            'percentage': percentage
        }

    def get_attendance_for_date(self, gregorian_date, session_type='שחרית'):
        """קבלת רשימת נוכחות לתאריך וסשן מסוים (כל התלמידים)

        Returns:
            List of tuples: [(student_id, date_hebrew, status), ...]
        """
        from pyluach import dates

        # Convert gregorian date to hebrew date string
        heb_date = dates.HebrewDate.from_pydate(gregorian_date)
        date_hebrew = heb_date.hebrew_date_string()

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT student_id, date_hebrew, status
            FROM attendance
            WHERE date_hebrew = ? AND session_type = ?
        ''', (date_hebrew, session_type))
        results = cursor.fetchall()
        conn.close()

        return results

    def get_all_sessions(self):
        """קבלת כל הסשנים (תפילות + סדרי לימוד)

        Returns:
            List of dicts with session info
        """
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, session_name, category, display_order, icon, active_days
            FROM session_definitions
            ORDER BY display_order
        ''')

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # המרת active_days מ-JSON למערך
        import json
        for session in results:
            session['active_days'] = json.loads(session['active_days'])

        return results

    def get_sessions_for_date(self, weekday):
        """קבלת סשנים פעילים ליום מסוים

        Args:
            weekday: 0=ראשון, 1=שני, ..., 6=שבת

        Returns:
            List of active sessions for this day
        """
        import json
        all_sessions = self.get_all_sessions()

        # סינון לפי יום
        active_sessions = [
            session for session in all_sessions
            if weekday in session['active_days']
        ]

        return active_sessions

    def get_sessions_by_category(self, category):
        """קבלת סשנים לפי קטגוריה

        Args:
            category: 'תפילה' או 'לימוד'

        Returns:
            List of sessions in this category
        """
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, session_name, category, display_order, icon, active_days
            FROM session_definitions
            WHERE category = ?
            ORDER BY display_order
        ''', (category,))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # המרת active_days מ-JSON למערך
        import json
        for session in results:
            session['active_days'] = json.loads(session['active_days'])

        return results

# ===== Exam Management Database Operations =====

class ExamDatabase(YeshivaDatabase):
    """מחלקה לניהול מבחנים - מורשת מ-YeshivaDatabase"""

    # ===== ניהול הספקים (Syllabi) =====

    def save_syllabus(self, grade, subject, syllabus_data, academic_year, semester):
        """שמירת הספקים למקצוע"""
        import json
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO subject_syllabi
            (grade, subject, masechet, daf_start, daf_end, chumash, chapter_start,
             chapter_end, halacha_section, siman_start, siman_end, target_exam_date,
             academic_year, semester, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            grade, subject,
            syllabus_data.get('masechet'), syllabus_data.get('daf_start'), syllabus_data.get('daf_end'),
            syllabus_data.get('chumash'), syllabus_data.get('chapter_start'), syllabus_data.get('chapter_end'),
            syllabus_data.get('halacha_section'), syllabus_data.get('siman_start'), syllabus_data.get('siman_end'),
            syllabus_data.get('target_exam_date'),
            academic_year, semester, datetime.now()
        ))

        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_syllabi(self, grade=None, subject=None, academic_year=None):
        """קבלת הספקים"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        query = 'SELECT * FROM subject_syllabi WHERE 1=1'
        params = []

        if grade:
            query += ' AND grade = ?'
            params.append(grade)
        if subject:
            query += ' AND subject = ?'
            params.append(subject)
        if academic_year:
            query += ' AND academic_year = ?'
            params.append(academic_year)

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        return results

    # ===== ניהול מבחנים =====

    def create_exam(self, exam_data, questions):
        """יצירת מבחן חדש"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # יצירת המבחן
        cursor.execute('''
            INSERT INTO exams (subject, title, description, syllabus_text, grade,
                             total_points, created_by, academic_year, semester, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            exam_data.get('subject'), exam_data.get('title'), exam_data.get('description'),
            exam_data.get('syllabus_text'), exam_data.get('grade'),
            exam_data.get('total_points', 100), exam_data.get('created_by'),
            exam_data.get('academic_year'), exam_data.get('semester'),
            exam_data.get('status', 'draft')
        ))

        exam_id = cursor.lastrowid

        # הוספת שאלות
        for q in questions:
            cursor.execute('''
                INSERT INTO exam_questions (exam_id, question_number, question_text,
                                          points, question_type, correct_answer)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                exam_id, q.get('question_number'), q.get('question_text'),
                q.get('points', 10), q.get('question_type', 'essay'),
                q.get('correct_answer')
            ))

        conn.commit()
        conn.close()
        return exam_id

    def get_exam(self, exam_id):
        """קבלת פרטי מבחן"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # מאפשר גישה לעמודות לפי שם
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM exams WHERE id = ?', (exam_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def get_exam_questions(self, exam_id):
        """קבלת שאלות מבחן"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM exam_questions
            WHERE exam_id = ?
            ORDER BY question_number
        ''', (exam_id,))

        questions = cursor.fetchall()
        conn.close()

        return questions

    def get_all_exams(self, grade=None, subject=None, status=None):
        """קבלת כל המבחנים"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        query = 'SELECT * FROM exams WHERE 1=1'
        params = []

        if grade:
            query += ' AND grade = ?'
            params.append(grade)
        if subject:
            query += ' AND subject = ?'
            params.append(subject)
        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY created_at DESC'

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        return results

    # ===== הקצאת מבחנים לתלמידים =====

    def assign_exam_to_students(self, exam_id, student_ids, scheduled_date, version_code='A'):
        """הקצאת מבחן לתלמידים"""
        import json
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # קבלת או יצירת גרסה
        cursor.execute('''
            SELECT id FROM exam_versions WHERE exam_id = ? AND version_code = ?
        ''', (exam_id, version_code))

        version = cursor.fetchone()
        if not version:
            cursor.execute('''
                INSERT INTO exam_versions (exam_id, version_code)
                VALUES (?, ?)
            ''', (exam_id, version_code))
            version_id = cursor.lastrowid
        else:
            version_id = version[0]

        # הקצאה לתלמידים
        assigned_ids = []
        for student_id in student_ids:
            qr_data = json.dumps({
                'student_id': student_id,
                'exam_id': exam_id,
                'version': version_code,
                'date': scheduled_date
            })

            cursor.execute('''
                INSERT OR REPLACE INTO student_exams
                (student_id, exam_id, version_id, scheduled_date, qr_code_data, status)
                VALUES (?, ?, ?, ?, ?, 'scheduled')
            ''', (student_id, exam_id, version_id, scheduled_date, qr_data))

            assigned_ids.append(cursor.lastrowid)

        conn.commit()
        conn.close()
        return assigned_ids

    def get_student_exams(self, student_id=None, exam_id=None):
        """קבלת מבחנים של תלמיד/ים"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        query = '''
            SELECT se.*, e.title, e.subject, e.total_points,
                   s.first_name, s.last_name
            FROM student_exams se
            JOIN exams e ON se.exam_id = e.id
            JOIN students s ON se.student_id = s.id
            WHERE 1=1
        '''
        params = []

        if student_id:
            query += ' AND se.student_id = ?'
            params.append(student_id)
        if exam_id:
            query += ' AND se.exam_id = ?'
            params.append(exam_id)

        query += ' ORDER BY se.scheduled_date DESC'

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        return results

    def postpone_exam(self, student_exam_id, new_date, reason):
        """דחיית מבחן"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE student_exams
            SET status = 'postponed',
                postponed_to_date = ?,
                postponement_reason = ?
            WHERE id = ?
        ''', (new_date, reason, student_exam_id))

        conn.commit()
        conn.close()

    # ===== ציונים =====

    def save_exam_grade(self, student_exam_id, total_score, graded_by,
                       grading_method='manual', ocr_confidence=None, notes=None):
        """שמירת ציון מבחן"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # קבלת נקודות כוללות
        cursor.execute('''
            SELECT e.total_points
            FROM student_exams se
            JOIN exams e ON se.exam_id = e.id
            WHERE se.id = ?
        ''', (student_exam_id,))

        result = cursor.fetchone()
        if not result:
            conn.close()
            return None

        total_points = result[0]
        grade_percent = (total_score / total_points * 100) if total_points > 0 else 0

        cursor.execute('''
            INSERT INTO exam_grades
            (student_exam_id, total_score, grade_percent, graded_by,
             grading_method, ocr_confidence, graded_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_exam_id, total_score, grade_percent, graded_by,
            grading_method, ocr_confidence, datetime.now(), notes
        ))

        grade_id = cursor.lastrowid

        # עדכון סטטוס המבחן
        cursor.execute('''
            UPDATE student_exams
            SET status = 'graded', actual_date = ?
            WHERE id = ?
        ''', (datetime.now().date(), student_exam_id))

        conn.commit()
        conn.close()
        return grade_id

    def get_student_grades(self, student_id):
        """קבלת כל הציונים של תלמיד"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT e.title, e.subject, se.scheduled_date, se.actual_date,
                   eg.total_score, eg.grade_percent, se.status, e.total_points
            FROM student_exams se
            JOIN exams e ON se.exam_id = e.id
            LEFT JOIN exam_grades eg ON eg.student_exam_id = se.id
            WHERE se.student_id = ?
            ORDER BY se.scheduled_date DESC
        ''', (student_id,))

        results = cursor.fetchall()
        conn.close()
        return results

    def get_exam_statistics(self, exam_id):
        """קבלת סטטיסטיקות מבחן"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as total_students,
                COUNT(eg.id) as graded_count,
                AVG(eg.grade_percent) as avg_percent,
                MIN(eg.grade_percent) as min_percent,
                MAX(eg.grade_percent) as max_percent
            FROM student_exams se
            LEFT JOIN exam_grades eg ON eg.student_exam_id = se.id
            WHERE se.exam_id = ?
        ''', (exam_id,))

        result = cursor.fetchone()
        conn.close()
        return result

    def get_grade_distribution(self, exam_id):
        """קבלת התפלגות ציונים"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT eg.grade_percent, COUNT(*) as count
            FROM exam_grades eg
            JOIN student_exams se ON se.id = eg.student_exam_id
            WHERE se.exam_id = ?
            GROUP BY CAST(eg.grade_percent / 10 AS INT) * 10
            ORDER BY eg.grade_percent
        ''', (exam_id,))

        results = cursor.fetchall()
        conn.close()
        return results
