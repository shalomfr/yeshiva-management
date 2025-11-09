# -*- coding: utf-8 -*-
"""
דגם תלמיד - Student Data Model
"""


class Student:
    """מחלקה המייצגת תלמיד"""

    def __init__(self, student_id=None, first_name="", last_name="", id_number="",
                 birth_date_hebrew="", address="", city="", father_name="", father_id_number="",
                 mother_name="", mother_id_number="", father_phone="", mother_phone="",
                 home_phone="", entry_date_hebrew="", current_grade="", initial_grade="",
                 status="פעיל", framework_type="רגיל", notes="", created_at=None,
                 last_grade_update=None):

        self.id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.id_number = id_number
        self.birth_date_hebrew = birth_date_hebrew
        self.address = address
        self.city = city
        self.father_name = father_name
        self.father_id_number = father_id_number
        self.mother_name = mother_name
        self.mother_id_number = mother_id_number
        self.father_phone = father_phone
        self.mother_phone = mother_phone
        self.home_phone = home_phone
        self.entry_date_hebrew = entry_date_hebrew
        self.current_grade = current_grade
        self.initial_grade = initial_grade
        self.status = status
        self.framework_type = framework_type
        self.notes = notes
        self.created_at = created_at
        self.last_grade_update = last_grade_update

    def get_full_name(self):
        """קבלת שם מלא"""
        return f"{self.first_name} {self.last_name}"

    def is_active(self):
        """בדיקה אם התלמיד פעיל"""
        return self.status == "פעיל"

    def to_dict(self):
        """המרה לדיקשנרי"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'id_number': self.id_number,
            'birth_date_hebrew': self.birth_date_hebrew,
            'address': self.address,
            'city': self.city,
            'father_name': self.father_name,
            'father_id_number': self.father_id_number,
            'mother_name': self.mother_name,
            'mother_id_number': self.mother_id_number,
            'father_phone': self.father_phone,
            'mother_phone': self.mother_phone,
            'home_phone': self.home_phone,
            'entry_date_hebrew': self.entry_date_hebrew,
            'current_grade': self.current_grade,
            'initial_grade': self.initial_grade,
            'status': self.status,
            'framework_type': self.framework_type,
            'notes': self.notes,
            'created_at': self.created_at,
            'last_grade_update': self.last_grade_update
        }

    @staticmethod
    def from_db_row(row):
        """יצירת Student מ-database row"""
        return Student(
            student_id=row[0],
            first_name=row[1],
            last_name=row[2],
            id_number=row[3],
            birth_date_hebrew=row[4],
            address=row[5],
            city=row[6],
            father_name=row[7],
            father_id_number=row[8],
            mother_name=row[9],
            mother_id_number=row[10],
            father_phone=row[11],
            mother_phone=row[12],
            home_phone=row[13],
            entry_date_hebrew=row[14],
            current_grade=row[15],
            initial_grade=row[16],
            status=row[17],
            framework_type=row[18],
            notes=row[19],
            created_at=row[20],
            last_grade_update=row[21]
        )
