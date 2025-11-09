"""
Test PDF generation
"""

from services.database import ExamDatabase, YeshivaDatabase
from services.pdf_generator import generate_exam_pdf_for_student

# Initialize databases
exam_db = ExamDatabase()
yeshiva_db = YeshivaDatabase()

# Get first exam and student
exams = exam_db.get_all_exams()
if not exams:
    print("No exams found!")
    exit(1)

exam_id = exams[0][0]
print(f"Testing with exam ID: {exam_id}")

# Get first student
students = yeshiva_db.get_all_students()
if not students:
    print("No students found!")
    exit(1)

student_id = students[0][0]
print(f"Testing with student ID: {student_id}, Name: {students[0][1]} {students[0][2]}")

# Try to generate PDF
try:
    print("Generating PDF...")
    pdf_bytes = generate_exam_pdf_for_student(exam_id, student_id, exam_db)

    # Save to file
    output_file = "test_exam.pdf"
    with open(output_file, 'wb') as f:
        f.write(pdf_bytes)

    print(f"PDF generated successfully! Saved to: {output_file}")
    print(f"File size: {len(pdf_bytes)} bytes")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
