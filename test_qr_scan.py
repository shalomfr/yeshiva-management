#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test QR Code scanning from PDF
"""

import json
from PIL import Image
from pyzbar import pyzbar
import qrcode

def test_qr_generation_and_reading():
    """בדיקה שה-QR נוצר ונקרא נכון"""

    print("\n=== בדיקה 1: יצירת וקריאת QR Code ===")

    # המידע לקידוד
    data = {
        'student_id': 45,
        'exam_id': 9,
        'date': '2025-01-07',
        'student_name': 'כהן משה',
        'exam_title': 'מבחן מתמטיקה'
    }

    # קידוד ל-JSON
    qr_data = json.dumps(data, ensure_ascii=False)
    print(f"נתונים מקוריים: {data}")

    # יצירת QR עם אותן הגדרות מהקוד
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=5,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # יצירת תמונה
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("test_qr.png")
    print("QR נשמר כ-test_qr.png")

    # קריאה בחזרה - טוען מחדש מהקובץ
    print("\n=== קריאת ה-QR שנוצר ===")
    img_loaded = Image.open("test_qr.png")
    codes = pyzbar.decode(img_loaded)

    if codes:
        print(f"[V] נמצאו {len(codes)} קודים")
        for code in codes:
            decoded_data = code.data.decode('utf-8')
            print(f"  סוג: {code.type}")
            print(f"  נתונים גולמיים: {decoded_data}")

            # פענוח JSON
            try:
                parsed = json.loads(decoded_data)
                print(f"  נתונים מפוענחים: {parsed}")
                print("  [V] הצלחה! QR עובד מושלם")
            except:
                print("  [X] בעיה בפענוח JSON")
    else:
        print("[X] לא נמצאו קודים!")

    return len(codes) > 0


def test_pdf_with_qr():
    """בדיקה של יצירת PDF עם QR ובדיקתו"""

    print("\n\n=== בדיקה 2: יצירת PDF עם QR Code ===")

    from services.pdf_generator import ExamPDFGenerator

    # יצירת PDF לדוגמה
    generator = ExamPDFGenerator()

    exam_data = {
        'id': 9,
        'subject': 'מתמטיקה',
        'title': 'מבחן סוף שנה',
        'description': 'מבחן מסכם',
        'syllabus_text': 'חומר הלימוד',
        'grade': 'י',
        'total_points': 100
    }

    questions = [
        {
            'question_number': 1,
            'question_text': 'מה זה 1+1?',
            'points': 10,
            'question_type': 'open',
            'options': None
        }
    ]

    student_data = {
        'id': 45,
        'name': 'כהן משה',
        'id_number': '123456789',
        'version': 'A'
    }

    print("יוצר PDF עם QR...")
    pdf_bytes = generator.create_exam_pdf(exam_data, questions, student_data)

    # שמירה
    with open("test_exam_qr.pdf", "wb") as f:
        f.write(pdf_bytes)

    print("PDF נשמר כ-test_exam_qr.pdf")

    # נסה לקרוא את ה-QR מה-PDF
    print("\n=== קריאת QR מה-PDF ===")
    import fitz  # PyMuPDF

    doc = fitz.open("test_exam_qr.pdf")
    page = doc[0]

    # המרה לתמונה
    zoom = 4  # רזולוציה גבוהה
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)

    # שמירה כתמונה
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))
    img.save("test_pdf_page.png")
    print(f"גודל תמונה: {img.size}")

    # חיפוש QR
    codes = pyzbar.decode(img)

    if codes:
        print(f"[V] נמצאו {len(codes)} קודים ב-PDF!")
        for code in codes:
            decoded_data = code.data.decode('utf-8')
            print(f"  סוג: {code.type}")
            try:
                parsed = json.loads(decoded_data)
                print(f"  נתונים: {parsed}")
                print("  [V] הצלחה! QR ב-PDF נקרא מושלם!")
                return True
            except:
                print(f"  נתונים גולמיים: {decoded_data}")
    else:
        print("[X] לא נמצאו קודים ב-PDF!")
        return False


if __name__ == "__main__":
    import io

    print("=" * 60)
    print("בדיקת QR Code במערכת המבחנים")
    print("=" * 60)

    # בדיקה 1
    success1 = test_qr_generation_and_reading()

    # בדיקה 2
    success2 = test_pdf_with_qr()

    print("\n" + "=" * 60)
    print("סיכום:")
    print(f"  יצירת וקריאת QR: {'[V] עובד' if success1 else '[X] לא עובד'}")
    print(f"  QR ב-PDF: {'[V] עובד' if success2 else '[X] לא עובד'}")
    print("=" * 60)