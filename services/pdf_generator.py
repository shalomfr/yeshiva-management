"""
PDF Generator Service for Exams
Generates exam PDFs with QR codes for automatic identification
"""

import os
import io
import json
import qrcode
import barcode
from barcode.writer import ImageWriter
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_CENTER

class ExamPDFGenerator:
    """מחלקה ליצירת PDFs של מבחנים עם QR codes"""

    def __init__(self):
        """אתחול המחלקה"""
        self.page_width, self.page_height = A4
        self.margin = 2 * cm

        # טעינת פונט עברי
        self.hebrew_font = None
        try:
            import os

            # נסה לטעון פונט Arial מ-Windows (תומך RTL מעולה עם bidi)
            windows_fonts = [
                r'C:\Windows\Fonts\arial.ttf',
                r'C:\Windows\Fonts\ARIAL.TTF',
                r'C:\Windows\Fonts\arialbd.ttf',
                r'C:\Windows\Fonts\ARIALBD.TTF'
            ]

            for font_path in windows_fonts:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('HebrewFont', font_path))
                    self.hebrew_font = 'HebrewFont'
                    print(f"Loaded Hebrew font from Windows: {font_path}")
                    break

            # אם לא נמצא David, נסה את הפונטים מהפרויקט
            if not self.hebrew_font:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                fonts_dir = os.path.join(base_dir, 'fonts')

                font_files = ['ARISTOCRATBOLD.TTF', 'ARISTORE.TTF', 'ARISBL.TTF']

                for font_file in font_files:
                    font_path = os.path.join(fonts_dir, font_file)
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('HebrewFont', font_path))
                        self.hebrew_font = 'HebrewFont'
                        print(f"Loaded Hebrew font from project: {font_file}")
                        break

            if not self.hebrew_font:
                print(f"Warning: No Hebrew fonts found")
        except Exception as e:
            print(f"Warning: Could not load Hebrew font: {e}")
            pass

    def prepare_hebrew_text(self, text):
        """
        הכנת טקסט עברי להצגה ב-PDF
        מטפל בטקסט עם נקודתיים (label: value) וגם עם תגיות HTML

        Args:
            text: טקסט לעיבוד

        Returns:
            טקסט מעובד
        """
        if not text:
            return text

        try:
            from bidi.algorithm import get_display
            import re

            # טיפול מיוחד בתבנית: <b>label:</b> value
            # זה הפורמט הנפוץ שלנו
            bold_pattern = r'<b>(.*?):</b>\s*(.*?)$'
            match = re.match(bold_pattern, text)

            if match:
                # יש תבנית של <b>label:</b> value
                label = match.group(1).strip()
                value = match.group(2).strip()

                # הפוך כל חלק בנפרד
                label_display = get_display(label)
                value_display = get_display(value) if value else ''

                # החזר בפורמט הנכון עם תגיות במקום הנכון
                return f"<b>{value_display} :{label_display}</b>"

            # אם זה לא התבנית הזו, טפל בצורה רגילה
            # קודם הוצא תגיות
            text_no_tags = re.sub(r'<[^>]+>', '', text)

            # אם יש נקודתיים, טפל בתווית וערך בנפרד
            if ':' in text_no_tags:
                parts = text_no_tags.split(':', 1)
                label = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ''

                label_display = get_display(label)
                value_display = get_display(value) if value else ''

                # אם יש תגיות <b> בטקסט המקורי, החזר אותן
                if '<b>' in text:
                    return f"<b>{value_display} :{label_display}</b>"
                else:
                    return f"{value_display} :{label_display}"
            else:
                # טקסט רגיל ללא נקודתיים
                result = get_display(text_no_tags)

                # אם יש תגיות במקור, החזר אותן
                if '<b>' in text and '</b>' in text:
                    return f"<b>{result}</b>"
                return result

        except ImportError:
            # אם אין bidi, נחזיר כמו שהוא (לא יהיה נכון)
            print("Warning: python-bidi not found. Hebrew text may not display correctly.")
            return text

    def generate_barcode(self, data, width=3.5, height=3.5):
        """
        יצירת QR Code - עמיד הרבה יותר לסריקה אחרי הדפסה!

        Args:
            data: המידע לקידוד (dict או string)
            width: רוחב ב-cm (ברירת מחדל 3.5cm)
            height: גובה ב-cm (ברירת מחדל 3.5cm)

        Returns:
            Image object של reportlab
        """
        import qrcode
        import json

        # המרה לפורמט JSON עבור QR
        if isinstance(data, dict):
            # קידוד כל הנתונים ל-JSON
            qr_data = json.dumps({
                'student_id': data.get('student_id', 0),
                'exam_id': data.get('exam_id', 0),
                'date': data.get('date', ''),
                'student_name': data.get('student_name', ''),
                'exam_title': data.get('exam_title', '')
            }, ensure_ascii=False)  # תמיכה בעברית
        else:
            qr_data = str(data)

        # יצירת QR Code עם הגדרות מקסימליות לעמידות
        qr = qrcode.QRCode(
            version=4,  # גודל 33x33 מודולים - מאזן בין גודל לעמידות
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% תיקון שגיאות!
            box_size=12,  # גודל כל ריבוע - גדול יותר = קל יותר לסריקה
            border=5,  # שוליים רחבים לסריקה קלה
        )

        qr.add_data(qr_data)
        qr.make(fit=True)

        # יצירת תמונה בשחור-לבן עם ניגודיות מקסימלית
        img = qr.make_image(fill_color="black", back_color="white")

        # שמירה ל-BytesIO בפורמט PNG
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # יצירת Image object של reportlab
        return Image(img_buffer, width=width*cm, height=height*cm)

    def create_exam_pdf(self, exam_data, questions, student_data, output_path=None):
        """
        יצירת PDF של מבחן לתלמיד ספציפי

        Args:
            exam_data: dict עם פרטי המבחן
            questions: list של שאלות
            student_data: dict עם פרטי התלמיד
            output_path: נתיב לשמירה (אופציונלי)

        Returns:
            bytes של ה-PDF או None אם נשמר לקובץ
        """
        # יצירת buffer או קובץ
        if output_path:
            pdf_buffer = output_path
        else:
            pdf_buffer = io.BytesIO()

        # יצירת המסמך
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )

        # סגנונות
        styles = self._create_styles()

        # אלמנטים של ה-PDF
        story = []

        # כותרת ראשית
        story.append(Paragraph(self.prepare_hebrew_text("מבחן"), styles['Title']))
        story.append(Spacer(1, 0.3*cm))

        # פרטי המבחן - עטיפה של כל השורה ביחד
        title = exam_data.get('title', '')
        subject = exam_data.get('subject', '')
        grade = exam_data.get('grade', '')

        story.append(Paragraph(self.prepare_hebrew_text(f"<b>שם המבחן:</b> {title}"), styles['RightAligned']))
        story.append(Paragraph(self.prepare_hebrew_text(f"<b>מקצוע:</b> {subject}"), styles['RightAligned']))
        story.append(Paragraph(self.prepare_hebrew_text(f"<b>שיעור:</b> {grade}"), styles['RightAligned']))

        if exam_data.get('scheduled_date'):
            date = exam_data.get('scheduled_date', '')
            story.append(Paragraph(self.prepare_hebrew_text(f"<b>תאריך:</b> {date}"), styles['RightAligned']))

        story.append(Spacer(1, 0.5*cm))

        # פרטי התלמיד ו-QR code
        student_qr_data = {
            'student_id': student_data.get('id'),
            'exam_id': exam_data.get('id'),
            'student_name': student_data.get('name'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'version': student_data.get('version', 'A')
        }

        # QR Code - גדול יותר לסריקה קלה יותר!
        barcode_image = self.generate_barcode(student_qr_data, width=4, height=4)

        # טבלה עם פרטי תלמיד ו-QR
        student_name = student_data.get('name', '')
        id_number = student_data.get('id_number', '_______________')

        student_table_data = [
            [
                Paragraph(self.prepare_hebrew_text(f"<b>שם התלמיד:</b> {student_name}"), styles['RightAligned']),
                barcode_image
            ],
            [
                Paragraph(self.prepare_hebrew_text(f"<b>תעודת זהות:</b> {id_number}"), styles['RightAligned']),
                ''
            ]
        ]

        student_table = Table(student_table_data, colWidths=[9*cm, 8*cm])
        student_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('SPAN', (1, 1), (1, 1)),
        ]))

        story.append(student_table)
        story.append(Spacer(1, 0.7*cm))

        # הוראות
        if exam_data.get('description'):
            description = exam_data.get('description', '')
            story.append(Paragraph(self.prepare_hebrew_text("<b>הוראות:</b>"), styles['RightAligned']))
            story.append(Paragraph(self.prepare_hebrew_text(description), styles['RightAligned']))
            story.append(Spacer(1, 0.5*cm))

        # קו מפריד
        story.append(Paragraph("_" * 100, styles['Centered']))
        story.append(Spacer(1, 0.5*cm))

        # שאלות
        total_points = 0
        for i, question in enumerate(questions, 1):
            points = question.get('points', 0)
            total_points += points

            # מספר שאלה ונקודות
            q_header = self.prepare_hebrew_text(f"<b>שאלה {i}</b> ({points} נקודות)")
            story.append(Paragraph(q_header, styles['QuestionHeader']))
            story.append(Spacer(1, 0.2*cm))

            # טקסט השאלה
            question_text = question.get('question_text', '')
            story.append(Paragraph(self.prepare_hebrew_text(question_text), styles['Question']))
            story.append(Spacer(1, 0.3*cm))

            # אם זו שאלת רב ברירה
            if question.get('question_type') == 'multiple_choice' and question.get('options'):
                try:
                    options = json.loads(question.get('options', '[]')) if isinstance(question.get('options'), str) else question.get('options', [])
                    for j, option in enumerate(options, 1):
                        if option:  # רק אם האופציה לא ריקה
                            option_line = f"    {j}. {option}"
                            story.append(Paragraph(self.prepare_hebrew_text(option_line), styles['RightAligned']))
                except:
                    pass

                story.append(Spacer(1, 0.2*cm))
                story.append(Paragraph(self.prepare_hebrew_text("תשובה: _______"), styles['RightAligned']))
            else:
                # שאלה פתוחה - מקום לתשובה
                answer_lines = max(3, int(points / 5))  # מספר שורות לפי נקודות

                for _ in range(answer_lines):
                    story.append(Spacer(1, 0.7*cm))
                    story.append(Paragraph("_" * 100, styles['RightAligned']))

            story.append(Spacer(1, 0.7*cm))

            # מעבר עמוד אם צריך (כל 3-4 שאלות)
            if i % 3 == 0 and i < len(questions):
                story.append(PageBreak())

        # סיכום נקודות
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph("_" * 100, styles['Centered']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(self.prepare_hebrew_text(f"<b>סה\"כ נקודות במבחן: {total_points}</b>"), styles['Centered']))
        story.append(Paragraph(self.prepare_hebrew_text(f"<b>ציון שהתקבל: ______ / {total_points}</b>"), styles['Centered']))

        # בניית ה-PDF
        doc.build(story)

        # הוספת metadata ל-PDF עם פרטי התלמיד והמבחן
        # זה יישמר בתוך ה-PDF ונוכל לקרוא אותו בקלות בלי צורך בברקוד!
        try:
            from PyPDF2 import PdfReader, PdfWriter
            import json

            pdf_buffer.seek(0)
            reader = PdfReader(pdf_buffer)
            writer = PdfWriter()

            # העתק את כל העמודים
            for page in reader.pages:
                writer.add_page(page)

            # הוסף metadata מותאם אישית
            metadata = {
                '/Student_ID': str(student_data['id']),
                '/Student_Name': student_data['name'],
                '/Exam_ID': str(exam_data['id']),
                '/Exam_Title': exam_data['title'],
                '/YeshivaData': json.dumps({  # כל המידע בJSON
                    'student_id': student_data['id'],
                    'student_name': student_data['name'],
                    'exam_id': exam_data['id'],
                    'exam_title': exam_data['title'],
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'version': student_data.get('version', 'A')
                })
            }
            writer.add_metadata(metadata)

            # כתוב ל-buffer חדש
            final_buffer = io.BytesIO()
            writer.write(final_buffer)
            final_buffer.seek(0)

            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(final_buffer.getvalue())
                return None
            else:
                return final_buffer.getvalue()

        except Exception as e:
            print(f"Warning: Could not add metadata to PDF: {e}")
            # אם נכשל, החזר את ה-PDF המקורי
            if output_path:
                return None
            else:
                pdf_buffer.seek(0)
                return pdf_buffer.getvalue()

    def create_batch_exams(self, exam_data, questions, students_list, output_dir):
        """
        יצירת PDFs לכל התלמידים

        Args:
            exam_data: פרטי המבחן
            questions: רשימת שאלות
            students_list: רשימת תלמידים
            output_dir: תיקייה לשמירת הקבצים

        Returns:
            list של נתיבי הקבצים שנוצרו
        """
        # יצירת התיקייה אם לא קיימת
        os.makedirs(output_dir, exist_ok=True)

        created_files = []

        for student in students_list:
            # יצירת שם קובץ
            safe_name = student.get('name', 'student').replace(' ', '_')
            filename = f"exam_{exam_data.get('id')}_{student.get('id')}_{safe_name}.pdf"
            filepath = os.path.join(output_dir, filename)

            # יצירת ה-PDF
            self.create_exam_pdf(exam_data, questions, student, filepath)
            created_files.append(filepath)

        return created_files

    def _create_styles(self):
        """יצירת סגנונות לטקסט"""
        styles = getSampleStyleSheet()

        # סגנון בסיסי - הוספת פונט עברי
        if self.hebrew_font:
            styles['Normal'].fontName = self.hebrew_font
            styles['Normal'].wordWrap = 'RTL'

        # כותרת ראשית - עדכון הסגנון הקיים
        styles['Title'].fontSize = 24
        styles['Title'].alignment = TA_CENTER
        styles['Title'].spaceAfter = 12
        styles['Title'].textColor = colors.HexColor('#1a1a1a')
        styles['Title'].fontName = self.hebrew_font if self.hebrew_font else 'Helvetica-Bold'

        # טקסט מיושר לימין
        if 'RightAligned' not in styles:
            styles.add(ParagraphStyle(
                name='RightAligned',
                parent=styles['Normal'],
                fontSize=11,
                alignment=TA_RIGHT,
                spaceAfter=6,
                fontName=self.hebrew_font if self.hebrew_font else 'Helvetica'
            ))

        # טקסט ממורכז
        if 'Centered' not in styles:
            styles.add(ParagraphStyle(
                name='Centered',
                parent=styles['Normal'],
                fontSize=11,
                alignment=TA_CENTER,
                spaceAfter=6,
                fontName=self.hebrew_font if self.hebrew_font else 'Helvetica'
            ))

        # כותרת שאלה
        if 'QuestionHeader' not in styles:
            styles.add(ParagraphStyle(
                name='QuestionHeader',
                parent=styles['Normal'],
                fontSize=13,
                alignment=TA_RIGHT,
                spaceAfter=6,
                textColor=colors.HexColor('#2563eb'),
                fontName=self.hebrew_font if self.hebrew_font else 'Helvetica-Bold'
            ))

        # שאלה
        if 'Question' not in styles:
            styles.add(ParagraphStyle(
                name='Question',
                parent=styles['Normal'],
                fontSize=11,
                alignment=TA_RIGHT,
                spaceAfter=6,
                fontName=self.hebrew_font if self.hebrew_font else 'Helvetica'
            ))

        return styles


def generate_exam_pdf_for_student(exam_id, student_id, db):
    """
    פונקציית עזר ליצירת PDF למבחן ותלמיד ספציפיים

    Args:
        exam_id: מזהה המבחן
        student_id: מזהה התלמיד
        db: אובייקט ExamDatabase

    Returns:
        bytes של ה-PDF
    """
    # קבלת נתוני המבחן
    exam = db.get_exam(exam_id)
    if not exam:
        raise ValueError(f"מבחן {exam_id} לא נמצא")

    # exam הוא dictionary עכשיו, לא tuple
    exam_data = {
        'id': exam['id'],
        'subject': exam['subject'],
        'title': exam['title'],
        'description': exam.get('description', ''),
        'syllabus_text': exam.get('syllabus_text', ''),
        'grade': exam.get('grade', ''),
        'total_points': exam.get('total_points', 0)
    }

    # קבלת שאלות
    questions_raw = db.get_exam_questions(exam_id)
    questions = [{
        'question_number': q[2],
        'question_text': q[3],
        'points': q[4],
        'question_type': q[5],
        'options': q[6] if len(q) > 6 else None,
        'correct_answer': q[6] if q[5] == 'multiple_choice' and len(q) > 6 else None
    } for q in questions_raw]

    # קבלת נתוני התלמיד
    from services.database import YeshivaDatabase
    yeshiva_db = YeshivaDatabase()
    student = yeshiva_db.get_student(student_id)

    if not student:
        raise ValueError(f"תלמיד {student_id} לא נמצא")

    # student הוא dictionary עכשיו, לא tuple
    student_data = {
        'id': student['id'],
        'name': f"{student['last_name']} {student['first_name']}",  # שם משפחה + שם פרטי
        'id_number': student.get('id_number', ''),
        'version': 'A'
    }

    # יצירת ה-PDF
    generator = ExamPDFGenerator()
    return generator.create_exam_pdf(exam_data, questions, student_data)


def generate_batch_pdfs(exam_id, student_ids, output_dir, db):
    """
    יצירת PDFs לרשימת תלמידים

    Args:
        exam_id: מזהה המבחן
        student_ids: רשימת מזהי תלמידים
        output_dir: תיקייה לשמירה
        db: אובייקט ExamDatabase

    Returns:
        list של נתיבי קבצים שנוצרו
    """
    # קבלת נתונים
    exam = db.get_exam(exam_id)
    if not exam:
        raise ValueError(f"מבחן {exam_id} לא נמצא")

    # exam הוא dictionary עכשיו, לא tuple
    exam_data = {
        'id': exam['id'],
        'subject': exam['subject'],
        'title': exam['title'],
        'description': exam.get('description', ''),
        'syllabus_text': exam.get('syllabus_text', ''),
        'grade': exam.get('grade', ''),
        'total_points': exam.get('total_points', 0)
    }

    questions_raw = db.get_exam_questions(exam_id)
    questions = [{
        'question_number': q[2],
        'question_text': q[3],
        'points': q[4],
        'question_type': q[5],
        'options': q[6] if len(q) > 6 else None
    } for q in questions_raw]

    # קבלת נתוני תלמידים
    from services.database import YeshivaDatabase
    yeshiva_db = YeshivaDatabase()

    students_list = []
    for student_id in student_ids:
        student = yeshiva_db.get_student(student_id)
        if student:
            # student הוא dictionary עכשיו, לא tuple
            students_list.append({
                'id': student['id'],
                'name': f"{student['last_name']} {student['first_name']}",  # שם משפחה + שם פרטי
                'id_number': student.get('id_number', ''),
                'version': 'A'
            })

    # יצירת PDFs
    generator = ExamPDFGenerator()
    return generator.create_batch_exams(exam_data, questions, students_list, output_dir)
