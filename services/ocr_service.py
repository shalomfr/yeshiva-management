"""
OCR Service for Automated Grade Reading
Reads QR codes and grades from scanned exam PDFs
"""

import os
import re
import json
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pyzbar import pyzbar
import fitz  # PyMuPDF
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Optional

class ExamOCRService:
    """שירות OCR לקריאת מבחנים סרוקים"""

    def __init__(self, tesseract_path=None):
        """
        אתחול השירות

        Args:
            tesseract_path: נתיב ל-tesseract executable (אופציונלי)
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # הגדרות OCR
        self.tesseract_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789./'

    def preprocess_image(self, image):
        """
        עיבוד מקדים של תמונה לשיפור דיוק OCR

        Args:
            image: תמונה (numpy array)

        Returns:
            תמונה מעובדת
        """
        # המרה לגווני אפור
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # הגדלת ניגודיות
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # הסרת רעש
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)

        # סף (thresholding) אדפטיבי
        thresh = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )

        return thresh

    def deskew_image(self, image):
        """
        תיקון זווית הטיה של התמונה

        Args:
            image: תמונה (numpy array)

        Returns:
            תמונה מתוקנת
        """
        # זיהוי קווים
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

        if lines is None:
            return image

        # חישוב זווית ממוצעת
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta) - 90
            if abs(angle) < 45:
                angles.append(angle)

        if not angles:
            return image

        median_angle = np.median(angles)

        # סיבוב התמונה
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return rotated

    def read_pdf_metadata(self, pdf_path: str) -> Optional[Dict]:
        """
        קריאת metadata מ-PDF - פתרון יצירתי לבעיית הברקוד!

        Returns:
            dict עם פרטי התלמיד והמבחן, או None
        """
        try:
            from PyPDF2 import PdfReader
            import json

            print("="*50)
            print("DEBUG: Trying to read PDF metadata...")

            reader = PdfReader(pdf_path)
            metadata = reader.metadata

            if metadata:
                print(f"DEBUG: Found metadata fields: {list(metadata.keys())}")

                # חפש את המידע שלנו
                if '/YeshivaData' in metadata:
                    yeshiva_data = json.loads(metadata['/YeshivaData'])
                    print(f"DEBUG: SUCCESS! Found YeshivaData: {yeshiva_data}")
                    return yeshiva_data

                # נסה לבנות מה שיש
                if '/Student_ID' in metadata and '/Exam_ID' in metadata:
                    result = {
                        'student_id': int(metadata['/Student_ID']),
                        'exam_id': int(metadata['/Exam_ID']),
                        'student_name': metadata.get('/Student_Name', ''),
                        'exam_title': metadata.get('/Exam_Title', ''),
                        'date': metadata.get('/Date', '')
                    }
                    print(f"DEBUG: Built data from individual fields: {result}")
                    return result

            print("DEBUG: No YeshivaData in metadata")
            print("="*50)
            return None

        except Exception as e:
            print(f"DEBUG: Error reading metadata: {e}")
            print("="*50)
            return None

    def preprocess_for_qr(self, image_np):
        """
        עיבוד מקדים מיוחד ל-QR codes - יותר אגרסיבי!
        
        Args:
            image_np: תמונה (numpy array)
        
        Returns:
            list של תמונות מעובדות לניסיון
        """
        processed_images = []
        
        # המרה לגווני אפור
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_np
        
        # 1. התמונה המקורית באפור
        processed_images.append(("grayscale", gray))
        
        # 2. Adaptive threshold - מצוין ל-QR
        adaptive = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
        processed_images.append(("adaptive_threshold", adaptive))
        
        # 3. OTSU threshold
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(("otsu", otsu))
        
        # 4. עם sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        processed_images.append(("sharpened", sharpened))
        
        # 5. CLAHE לניגודיות
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        processed_images.append(("clahe", enhanced))
        
        return processed_images

    def read_qr_code(self, image) -> Optional[Dict]:
        """
        קריאת QR code או barcode מתמונה - גרסה משופרת ואגרסיבית!

        Args:
            image: תמונה (numpy array או PIL Image)

        Returns:
            dict עם המידע מה-QR/barcode או None
        """
        print("="*50)
        print("DEBUG: Starting barcode/QR detection")

        # המרה ל-PIL Image אם צריך
        if isinstance(image, np.ndarray):
            print(f"DEBUG: Converting numpy array to PIL. Shape: {image.shape}")
            pil_image = Image.fromarray(image)
        else:
            pil_image = image
            print(f"DEBUG: Already PIL Image. Size: {pil_image.size}")

        # שמירת תמונת debug
        try:
            debug_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp')
            os.makedirs(debug_dir, exist_ok=True)
            debug_path = os.path.join(debug_dir, f'debug_scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
            pil_image.save(debug_path)
            print(f"DEBUG: Saved debug image to {debug_path}")
        except Exception as e:
            print(f"DEBUG: Could not save debug image: {e}")

        # זיהוי QR codes ו-barcodes (כולל CODE128)
        print("DEBUG: Attempting pyzbar.decode on original image...")
        codes = pyzbar.decode(pil_image)

        print(f"DEBUG: Found {len(codes)} codes on original image")

        if not codes:
            print("DEBUG: No codes found on original. Trying multiple preprocessing methods...")
            # נסה שוב עם עיבודים מקדימים משופרים
            try:
                # המרה ל-numpy אם צריך
                if not isinstance(image, np.ndarray):
                    image_np = np.array(pil_image)
                else:
                    image_np = image

                print(f"DEBUG: Image array shape: {image_np.shape}, dtype: {image_np.dtype}")

                # נסה מספר שיטות עיבוד שונות
                processed_versions = self.preprocess_for_qr(image_np)
                
                for method_name, processed in processed_versions:
                    print(f"DEBUG: Trying method: {method_name}")
                    processed_pil = Image.fromarray(processed)
                    codes = pyzbar.decode(processed_pil)
                    print(f"DEBUG: Method {method_name} found {len(codes)} codes")
                    
                    if codes:
                        print(f"DEBUG: SUCCESS with method: {method_name}")
                        break
                
            except Exception as e:
                print(f"DEBUG: Preprocessing failed with error: {e}")
                import traceback
                traceback.print_exc()
        
        # אם pyzbar נכשל, נסה zxing-cpp (אם זמין)
        if not codes:
            try:
                import zxingcpp
                print("DEBUG: Trying zxing-cpp as fallback...")
                
                # המרה ל-numpy
                if not isinstance(image, np.ndarray):
                    image_np = np.array(pil_image)
                else:
                    image_np = image
                
                results = zxingcpp.read_barcodes(image_np)
                print(f"DEBUG: zxing-cpp found {len(results)} codes")
                
                if results and len(results) > 0:
                    # המר לפורמט של pyzbar
                    from types import SimpleNamespace
                    code = SimpleNamespace(
                        data=results[0].text.encode('utf-8'),
                        type=results[0].format.name,
                        quality=50,
                        rect=SimpleNamespace(left=0, top=0, width=0, height=0)
                    )
                    codes = [code]
                    print(f"DEBUG: zxing-cpp SUCCESS! Found {results[0].format.name}")
            except ImportError:
                print("DEBUG: zxing-cpp not available, skipping")
            except Exception as e:
                print(f"DEBUG: zxing-cpp failed: {e}")

        if not codes:
            print("DEBUG: FAILED - No codes found even after all attempts")
            print("="*50)
            return None

        # קריאת הראשון
        code = codes[0]
        code_data = code.data.decode('utf-8')
        code_type = code.type

        print(f"DEBUG: SUCCESS! Code type: {code_type}")
        print(f"DEBUG: Code data: {code_data}")
        print(f"DEBUG: Code quality: {code.quality}")
        print(f"DEBUG: Code rect: {code.rect}")
        print("="*50)

        try:
            # אם זה JSON (QR code ישן)
            return json.loads(code_data)
        except:
            # אם זה barcode בפורמט: StudentID-ExamID-Date
            if '-' in code_data:
                parts = code_data.split('-')
                print(f"DEBUG: Barcode parts: {parts}")
                if len(parts) >= 3:
                    result = {
                        'student_id': int(parts[0]) if parts[0].isdigit() else parts[0],
                        'exam_id': int(parts[1]) if parts[1].isdigit() else parts[1],
                        'date': f"{parts[2][:4]}-{parts[2][4:6]}-{parts[2][6:8]}" if len(parts[2]) == 8 else parts[2]
                    }
                    print(f"DEBUG: Parsed barcode result: {result}")
                    return result
            return {'raw_data': code_data}

    def extract_grade_region(self, image, region_keywords=['ציון', 'סה"כ', 'נקודות']):
        """
        חילוץ אזור הציון מהתמונה

        Args:
            image: תמונה מעובדת
            region_keywords: מילות מפתח לזיהוי אזור הציון

        Returns:
            תמונה של אזור הציון או None
        """
        # OCR מלא לזיהוי המיקום
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang='heb+eng')

        # חיפוש מילות המפתח
        grade_regions = []
        for i, text in enumerate(data['text']):
            if any(keyword in text for keyword in region_keywords):
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                # הרחבת האזור כלפי מטה (הציון בדרך כלל אחרי הכיתוב)
                grade_regions.append((x, y + h, w + 200, h + 50))

        if not grade_regions:
            # אם לא נמצא, קח את החלק התחתון של התמונה
            h, w = image.shape[:2]
            return image[int(h * 0.85):h, int(w * 0.3):int(w * 0.7)]

        # קח את האזור הראשון שנמצא
        x, y, w, h = grade_regions[0]
        return image[y:y+h, x:x+w]

    def read_grade_from_text(self, text: str) -> Optional[Dict]:
        """
        חילוץ ציון מטקסט

        Args:
            text: טקסט שהתקבל מ-OCR

        Returns:
            dict עם הציון והאמינות
        """
        # דפוסי חיפוש לציונים
        patterns = [
            r'(\d+)\s*/\s*(\d+)',  # 85 / 100
            r'(\d+)\s*מתוך\s*(\d+)',  # 85 מתוך 100
            r'(\d+)\s*:\s*(\d+)',  # 85:100
            r'ציון[:\s]*(\d+)',  # ציון: 85
            r'(\d{1,3})\s*(?:נקודות|נק)',  # 85 נקודות
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:
                    score = int(match.group(1))
                    total = int(match.group(2))
                    return {
                        'score': score,
                        'total': total,
                        'percentage': round((score / total) * 100, 2),
                        'confidence': 0.8
                    }
                else:
                    score = int(match.group(1))
                    return {
                        'score': score,
                        'total': None,
                        'percentage': None,
                        'confidence': 0.6
                    }

        # נסה לקרוא מספר בודד
        numbers = re.findall(r'\d+', text)
        if numbers:
            score = int(numbers[0])
            return {
                'score': score,
                'total': None,
                'percentage': None,
                'confidence': 0.4
            }

        return None

    def process_single_page(self, image) -> Dict:
        """
        עיבוד עמוד בודד של מבחן

        Args:
            image: תמונה של העמוד

        Returns:
            dict עם התוצאות
        """
        result = {
            'qr_data': None,
            'grade': None,
            'ocr_text': '',
            'confidence': 0,
            'errors': []
        }

        try:
            # המרה ל-numpy array אם צריך
            if isinstance(image, Image.Image):
                image = np.array(image)

            # תיקון הטיה
            try:
                image = self.deskew_image(image)
            except Exception as e:
                result['errors'].append(f'Deskew failed: {str(e)}')

            # קריאת QR code
            qr_data = self.read_qr_code(image)
            if qr_data:
                result['qr_data'] = qr_data
            else:
                result['errors'].append('No QR code found')

            # עיבוד מקדים
            processed = self.preprocess_image(image)

            # חילוץ אזור הציון
            grade_region = self.extract_grade_region(processed)

            # OCR על אזור הציון
            grade_text = pytesseract.image_to_string(
                grade_region,
                config=self.tesseract_config,
                lang='eng'
            )
            result['ocr_text'] = grade_text

            # חילוץ הציון
            grade_info = self.read_grade_from_text(grade_text)
            if grade_info:
                result['grade'] = grade_info
                result['confidence'] = grade_info['confidence']
            else:
                result['errors'].append('Could not extract grade from text')

        except Exception as e:
            result['errors'].append(f'Processing error: {str(e)}')

        return result

    def process_pdf(self, pdf_path: str, max_workers: int = 4) -> List[Dict]:
        """
        עיבוד PDF של מבחנים סרוקים

        Args:
            pdf_path: נתיב לקובץ PDF
            max_workers: מספר threads למקביליות

        Returns:
            list של תוצאות לכל עמוד
        """
        # תחילה, נסה לקרוא metadata מה-PDF (הפתרון היצירתי!)
        metadata_info = self.read_pdf_metadata(pdf_path)
        if metadata_info:
            print("SUCCESS! Found exam data in PDF metadata - no barcode needed!")
            # אם מצאנו metadata, נחזיר תוצאה מיידית בלי סריקה
            return [{
                'page_number': 1,
                'qr_data': metadata_info,
                'grade': {'score': '-', 'total': '-'},
                'confidence': 1.0,
                'metadata_source': True  # סימן שזה מmetadata
            }]

        # אם אין metadata, נמשיך עם הסריקה הרגילה
        print("No metadata found, falling back to barcode scanning...")

        # פתיחת ה-PDF
        doc = fitz.open(pdf_path)

        # עיבוד מקבילי של העמודים
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # שליחת כל עמוד לעיבוד
            future_to_page = {}
            for page_num in range(len(doc)):
                page = doc[page_num]

                # המרה לתמונה ברזולוציה גבוהה מאוד - זה קריטי לזיהוי QR!
                # QR code נוצר עם box_size=12 וborder=5, אז צריך רזולוציה גבוהה
                # ב-PDF סרוק, איכות יורדת, אז נקרא ברזולוציה מאוד גבוהה
                zoom = 10.0  # 720 DPI - רזולוציה מאוד גבוהה לסריקה

                matrix = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=matrix)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                print(f"DEBUG PDF: Processing page {page_num + 1}, Image size: {img.size}, DPI: {zoom * 72}, Zoom: {zoom}")

                # שליחה לעיבוד
                future = executor.submit(self.process_single_page, img)
                future_to_page[future] = page_num

            # איסוף תוצאות
            for future in as_completed(future_to_page):
                page_num = future_to_page[future]
                try:
                    result = future.result()
                    result['page_number'] = page_num + 1
                    results.append(result)
                except Exception as e:
                    results.append({
                        'page_number': page_num + 1,
                        'qr_data': None,
                        'grade': None,
                        'ocr_text': '',
                        'confidence': 0,
                        'errors': [f'Page processing failed: {str(e)}']
                    })

        doc.close()

        # מיון לפי מספר עמוד
        results.sort(key=lambda x: x['page_number'])

        return results

    def process_image_batch(self, image_paths: List[str], max_workers: int = 4) -> List[Dict]:
        """
        עיבוד אצווה של קבצי תמונה

        Args:
            image_paths: רשימת נתיבים לתמונות
            max_workers: מספר threads למקביליות

        Returns:
            list של תוצאות
        """
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {}

            for path in image_paths:
                # טעינת התמונה
                img = Image.open(path)
                future = executor.submit(self.process_single_page, img)
                future_to_path[future] = path

            # איסוף תוצאות
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    result['file_path'] = path
                    results.append(result)
                except Exception as e:
                    results.append({
                        'file_path': path,
                        'qr_data': None,
                        'grade': None,
                        'ocr_text': '',
                        'confidence': 0,
                        'errors': [f'Image processing failed: {str(e)}']
                    })

        return results


def save_grades_to_database(ocr_results: List[Dict], db, graded_by: str = 'OCR') -> Dict:
    """
    שמירת ציונים במסד הנתונים

    Args:
        ocr_results: תוצאות OCR
        db: אובייקט ExamDatabase
        graded_by: שם המדרג

    Returns:
        dict עם סטטיסטיקות השמירה
    """
    stats = {
        'total': len(ocr_results),
        'saved': 0,
        'failed': 0,
        'errors': []
    }

    for result in ocr_results:
        try:
            # בדיקה שיש QR data וציון
            if not result.get('qr_data') or not result.get('grade'):
                stats['failed'] += 1
                stats['errors'].append(f"Page {result.get('page_number', 'unknown')}: Missing QR or grade data")
                continue

            qr_data = result['qr_data']
            grade = result['grade']

            student_id = qr_data.get('student_id')
            exam_id = qr_data.get('exam_id')

            if not student_id or not exam_id:
                stats['failed'] += 1
                stats['errors'].append(f"Page {result.get('page_number', 'unknown')}: Invalid QR data")
                continue

            # חיפוש student_exam_id
            conn = db.connect()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id FROM student_exams
                WHERE student_id = ? AND exam_id = ?
                ORDER BY scheduled_date DESC
                LIMIT 1
            ''', (student_id, exam_id))

            row = cursor.fetchone()

            if not row:
                stats['failed'] += 1
                stats['errors'].append(f"Student {student_id} not assigned to exam {exam_id}")
                conn.close()
                continue

            student_exam_id = row[0]

            # שמירת הציון
            db.save_exam_grade(
                student_exam_id=student_exam_id,
                total_score=grade['score'],
                graded_by=graded_by,
                grading_method='ocr',
                ocr_confidence=result.get('confidence', 0),
                notes=f"OCR: {result.get('ocr_text', '')[:100]}"
            )

            stats['saved'] += 1
            conn.close()

        except Exception as e:
            stats['failed'] += 1
            stats['errors'].append(f"Error saving grade: {str(e)}")

    return stats


# פונקציות עזר לשימוש מהאפליקציה

def process_scanned_pdf(pdf_path: str, db) -> Dict:
    """
    עיבוד PDF סרוק ושמירת הציונים

    Args:
        pdf_path: נתיב ל-PDF
        db: ExamDatabase

    Returns:
        dict עם התוצאות והסטטיסטיקות
    """
    ocr = ExamOCRService()

    # עיבוד ה-PDF
    results = ocr.process_pdf(pdf_path)

    # שמירת הציונים
    save_stats = save_grades_to_database(results, db)

    return {
        'ocr_results': results,
        'save_stats': save_stats
    }


def process_scanned_images(image_paths: List[str], db) -> Dict:
    """
    עיבוד תמונות סרוקות ושמירת הציונים

    Args:
        image_paths: רשימת נתיבי תמונות
        db: ExamDatabase

    Returns:
        dict עם התוצאות והסטטיסטיקות
    """
    ocr = ExamOCRService()

    # עיבוד התמונות
    results = ocr.process_image_batch(image_paths)

    # שמירת הציונים
    save_stats = save_grades_to_database(results, db)

    return {
        'ocr_results': results,
        'save_stats': save_stats
    }
