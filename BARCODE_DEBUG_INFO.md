# מידע טכני לזיהוי ברקוד - Barcode Recognition Debug Info

## תיאור הבעיה
כאשר מעלים קובץ PDF סרוק של מבחן, המערכת לא מצליחה לזהות את הברקוד (Code128) שמודפס על המבחן.
התוצאה היא "לא זוהה" במקום פרטי התלמיד והמבחן.

## מה עובד ומה לא עובד

### ✅ מה שכן עובד:
1. **יצירת הברקוד** - הברקוד נוצר כראוי ב-PDF
2. **קריאת ברקוד מקובץ ישיר** - בדיקה ישירה של קובץ PDF שנוצר מראה שpyzbar מצליח לקרוא את הברקוד
3. **הורדת PDF** - כפתור "הורד PDF" עובד ומייצר PDF עם ברקוד
4. **שליפת נתוני תלמיד** - כאשר הברקוד נקרא, המערכת מצליחה לשלוף את שם התלמיד מבסיס הנתונים

### ❌ מה שלא עובד:
1. **קריאת ברקוד מקובץ סרוק מועלה** - כאשר משתמש סורק מבחן ומעלה את ה-PDF, הברקוד לא מזוהה
2. זה קורה דרך העלאה באתר בכתובת: `http://127.0.0.1:5000/exams/scan`

## המידע הטכני

### 1. פורמט הברקוד
```
סוג: Code128 (ברקוד חד-מימדי)
פורמט נתונים: StudentID-ExamID-Date
דוגמה: "45-9-20251107" (תלמיד 45, מבחן 9, תאריך 07/11/2025)
```

### 2. הגדרות יצירת הברקוד
```python
# מקובץ: services/pdf_generator.py
options = {
    'module_width': 0.5,    # עובי קווים במ"מ
    'module_height': 18,    # גובה קווים
    'quiet_zone': 4,        # שוליים
    'font_size': 11,        # גודל טקסט
    'text_distance': 5,     # מרחק טקסט מקווים
    'dpi': 600,            # רזולוציה גבוהה מאוד
    'write_text': True,    # כתוב מספר מתחת
}

# גודל בPDF
width = 8cm  (80mm)
height = 2.5cm (25mm)
```

### 3. תהליך קריאת הברקוד
```python
# מקובץ: services/ocr_service.py, שורות 104-190

1. קריאת PDF והמרה לתמונה (PyMuPDF/fitz)
2. ניסיון ראשון: pyzbar.decode() על התמונה המקורית
3. אם נכשל: עיבוד מקדים (preprocessing) - המרה לאפור, threshold, מציאת קווים
4. ניסיון שני: pyzbar.decode() על התמונה המעובדת
5. אם מצליח: פענוח הנתונים מהפורמט StudentID-ExamID-Date
6. שליפת שם התלמיד ושם המבחן מבסיס הנתונים
```

### 4. הדפסות DEBUG שהוספנו
עכשיו כשמעלים קובץ, השרת מדפיס:
```
==================================================
DEBUG: Starting barcode/QR detection
DEBUG: Converting numpy array to PIL. Shape: (xxx, xxx, 3)
DEBUG: Attempting pyzbar.decode on original image...
DEBUG: Found 0 codes on original image
DEBUG: No codes found on original. Trying preprocessing...
DEBUG: Image array shape: (xxx, xxx, 3), dtype: uint8
DEBUG: Applying preprocessing...
DEBUG: Preprocessed shape: (xxx, xxx), dtype: uint8
DEBUG: Attempting pyzbar.decode on preprocessed image...
DEBUG: After preprocessing, found 0 codes
DEBUG: FAILED - No codes found even after preprocessing
==================================================
```

### 5. בדיקה שעשינו והצליחה
```python
# קובץ: test_barcode_reading.py

# בדיקה ישירה של PDF שנוצר:
import fitz  # PyMuPDF
from pyzbar import pyzbar

# פתיחת PDF
doc = fitz.open("test_exam.pdf")
page = doc[0]

# המרה לתמונה ב-72 DPI
pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

# ניסיון קריאה
codes = pyzbar.decode(img)
# תוצאה: SUCCESS! מצא Code128 עם הנתונים הנכונים
```

## השערות למה זה לא עובד

### 1. רזולוציה נמוכה בהמרת PDF מועלה
- אולי כאשר משתמש מעלה PDF סרוק, ההמרה לתמונה נעשית ברזולוציה נמוכה מדי
- **איך לבדוק**: להדפיס את גודל התמונה (shape) בשרת ולהשוות לגודל בבדיקה הישירה
- **איפה לתקן**: `app.py` שורה 904, בפונקציה `ocr.process_pdf(filepath)`

### 2. איכות הסריקה
- אם המשתמש סורק ברזולוציה נמוכה (למשל 100 DPI), הברקוד יהיה מטושטש
- **פתרון**: להציע למשתמש לסרוק ב-300 DPI לפחות

### 3. עיוות או רעש בסריקה
- סריקה עלולה להוסיף רעש, צל, או עיוות שמפריע לזיהוי
- **פתרון אפשרי**: לשפר את פונקציית `preprocess_image()` לטפל טוב יותר בברקודים

### 4. מיקום הברקוד בעמוד
- אולי הברקוד נחתך או נמצא באזור שלא נבדק
- **איך לבדוק**: לשמור את התמונה שהמערכת רואה ולבדוק ידנית

### 5. בעיה בספרייה pyzbar
- ייתכן שצריך להתקין את ה-zbar הבסיסי (C library)
- **פתרון**: להתקין zbar-tools או libzbar

## קוד לבדיקה מהירה

### בדיקה 1: שמירת התמונה שהמערכת רואה
הוסף לקוד ב-`ocr_service.py` אחרי שורה 120:
```python
# שמור תמונה לבדיקה
debug_path = "C:/temp/debug_barcode_scan.png"
pil_image.save(debug_path)
print(f"DEBUG: Saved image to {debug_path}")
```
זה ישמור את התמונה המדויקת שהמערכת מנסה לקרוא. פתח אותה וודא שהברקוד נראה ברור.

### בדיקה 2: בדיקת רזולוציה
הוסף לקוד ב-`services/ocr_service.py` בפונקציה `process_pdf`:
```python
# אחרי המרת עמוד לתמונה
print(f"DEBUG PDF: Page {page_num}, Zoom: {zoom}, Image size: {img.size}")
```

### בדיקה 3: ניסיון עם DPI גבוה יותר
ב-`services/ocr_service.py`, מצא את השורה:
```python
zoom = 2.0  # DPI של 144 (72 * 2)
```
שנה ל:
```python
zoom = 4.0  # DPI של 288 (72 * 4)
```

## פתרונות אפשריים

### פתרון 1: שימוש בZXing במקום pyzbar
```python
# התקנה
pip install zxing-cpp

# שימוש
import zxingcpp

def read_barcode_zxing(image):
    results = zxingcpp.read_barcodes(image)
    if results:
        return results[0].text
    return None
```

### פתרון 2: העלאת DPI בהמרת PDF
```python
# ב-process_pdf
zoom = 4.0  # במקום 2.0
```

### פתרון 3: שיפור preprocessing
```python
def preprocess_for_barcode(image):
    # המרה לאפור
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Adaptive threshold במקום threshold רגיל
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    # הוספת contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(thresh)

    return enhanced
```

### פתרון 4: חזרה לQR Code
אם הברקוד ממש לא עובד, אפשר לחזור ל-QR code שהוא יותר עמיד בפני איכות נמוכה:
```python
# במקום Code128, להשתמש ב-QR
import qrcode

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # תיקון שגיאות גבוה
    box_size=10,
    border=4,
)
```

## איך להריץ בדיקה
1. הפעל את השרת: `python app.py`
2. גש ל: `http://127.0.0.1:5000/exams/scan`
3. העלה קובץ PDF סרוק
4. בדוק את הקונסול של השרת - תראה את כל הדפסות DEBUG
5. העתק את כל הפלט ושלח לי

## קבצים רלוונטיים
- `services/ocr_service.py` - קריאת ברקוד וOCR
- `services/pdf_generator.py` - יצירת הברקוד
- `app.py` - העלאת קבצים
- `test_barcode_reading.py` - בדיקה עצמאית

## תוצאות בדיקה ישירה
הבדיקה ב-`test_barcode_reading.py` הראתה:
```
=== Testing Barcode Generation ===
Found 1 codes
  Type: CODE128
  Data: 72-5-20251107
  SUCCESS! Barcode is readable

=== Testing Barcode Reading from: test_exam.pdf ===
Testing with 72 DPI (zoom=1):
   Found 1 codes
   Code #1:
     Type: CODE128
     Data: 72-6-20251107
     Quality: 3
```

**מסקנה**: הברקוד עצמו עובד מצוין. הבעיה היא בתהליך ההעלאה/המרה.

## איש קשר
אם יש שאלות, התקשר עם Claude Code AI Assistant
