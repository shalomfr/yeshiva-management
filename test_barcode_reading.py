"""
סקריפט בדיקה לקריאת Barcode מ-PDF
להעביר למתכנת לבדיקה
"""

import sys
from PIL import Image
from pyzbar import pyzbar
import fitz  # PyMuPDF

def test_barcode_reading(pdf_path):
    """
    בודק אם ניתן לקרוא barcode מ-PDF
    """

    print(f"\n=== Testing Barcode Reading from: {pdf_path} ===\n")

    # 1. בדיקת תמיכה של pyzbar
    print("1. Checking pyzbar support:")
    try:
        print(f"   pyzbar version: {pyzbar.__version__ if hasattr(pyzbar, '__version__') else 'Unknown'}")
        print(f"   External dependencies: {pyzbar.EXTERNAL_DEPENDENCIES if hasattr(pyzbar, 'EXTERNAL_DEPENDENCIES') else 'N/A'}")
    except Exception as e:
        print(f"   Error checking pyzbar: {e}")

    # 2. המרת PDF לתמונה
    print("\n2. Converting PDF to image:")
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]  # עמוד ראשון

        # נסה ברזולוציות שונות
        for zoom in [1, 2, 3, 4]:
            dpi = zoom * 72
            print(f"\n   Testing with {dpi} DPI (zoom={zoom}):")

            # המרה לתמונה
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            print(f"   Image size: {img.size}")

            # 3. ניסיון קריאת barcode
            codes = pyzbar.decode(img)
            print(f"   Found {len(codes)} codes")

            if codes:
                for i, code in enumerate(codes):
                    print(f"\n   Code #{i+1}:")
                    print(f"     Type: {code.type}")
                    print(f"     Data: {code.data.decode('utf-8')}")
                    print(f"     Quality: {code.quality}")
                    print(f"     Rect: {code.rect}")
                break  # מצאנו ברקוד, אפשר לעצור

        doc.close()

    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

    # 4. בדיקה ישירה מתמונה (אם קיימת)
    print("\n3. Testing direct image read:")
    try:
        # נסה לקרוא ישירות את התמונה המומרת
        img = Image.open(pdf_path.replace('.pdf', '.png'))
        codes = pyzbar.decode(img)
        print(f"   Found {len(codes)} codes from PNG")

        if codes:
            for code in codes:
                print(f"   Type: {code.type}, Data: {code.data.decode('utf-8')}")
    except Exception as e:
        print(f"   PNG not available or error: {e}")

    # 5. המלצות
    print("\n=== Recommendations ===")
    print("If no barcodes found:")
    print("1. Try increasing DPI (zoom)")
    print("2. Check if barcode is Code128 compatible")
    print("3. Verify barcode data format")
    print("4. Consider using QR code instead")
    print("\nIf barcodes found:")
    print("Update the OCR service to use the same zoom level")


def test_barcode_generation():
    """
    בודק שיצירת הברקוד עובדת
    """
    print("\n=== Testing Barcode Generation ===\n")

    try:
        from barcode import Code128
        from barcode.writer import ImageWriter
        import io

        # יצירת ברקוד דוגמה
        test_data = "72-5-20251107"
        print(f"Creating barcode with data: {test_data}")

        code128 = Code128(test_data, writer=ImageWriter())

        # שמירה לקובץ
        filename = code128.save('test_barcode', options={
            'module_width': 0.5,
            'module_height': 18,
            'quiet_zone': 4,
            'font_size': 11,
            'text_distance': 5,
            'dpi': 600,
            'write_text': True,
        })

        print(f"Barcode saved to: {filename}")

        # נסה לקרוא אותו
        print("\nTrying to read generated barcode:")
        img = Image.open(filename)
        codes = pyzbar.decode(img)

        print(f"Found {len(codes)} codes")
        if codes:
            for code in codes:
                print(f"  Type: {code.type}")
                print(f"  Data: {code.data.decode('utf-8')}")
                print(f"  SUCCESS! Barcode is readable")
        else:
            print("  FAILED! Barcode is not readable by pyzbar")
            print("  This indicates a compatibility issue with Code128")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # בדיקת יצירה וקריאה
    test_barcode_generation()

    # בדיקה מ-PDF
    pdf_file = "test_exam.pdf"
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]

    import os
    if os.path.exists(pdf_file):
        test_barcode_reading(pdf_file)
    else:
        print(f"\nPDF file not found: {pdf_file}")
        print("Usage: python test_barcode_reading.py [pdf_file]")
