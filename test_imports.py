#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
בדיקה מהירה שכל ה-imports עובדים
"""

print("Testing imports...")

try:
    print("1. Testing Flask imports...")
    from flask import Flask, render_template, request, jsonify, send_file
    print("   ✓ Flask OK")
    
    print("2. Testing database imports...")
    from services.database import YeshivaDatabase, ExamDatabase
    print("   ✓ Database OK")
    
    print("3. Testing OCR service imports...")
    from services.ocr_service import ExamOCRService
    print("   ✓ OCR Service OK")
    
    print("4. Testing PDF generator imports...")
    from services.pdf_generator import ExamPDFGenerator
    print("   ✓ PDF Generator OK")
    
    print("\n5. Creating OCR service instance...")
    ocr = ExamOCRService()
    print("   ✓ OCR Service created successfully")
    
    print("\n" + "="*50)
    print("✓ ALL IMPORTS SUCCESSFUL!")
    print("="*50)
    print("\nהשרת אמור לעבוד כעת.")
    print("הפעל: python app.py")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\nיש בעיה עם אחד מה-imports!")



