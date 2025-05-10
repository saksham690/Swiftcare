from flask import Flask, request, jsonify
from faker import Faker
import sqlite3
from datetime import datetime

app = Flask(__name__)
fake = Faker()

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('lab_reports.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lab_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_email TEXT NOT NULL,
            doctor_id INTEGER NOT NULL,
            doctor_speciality TEXT NOT NULL,
            report_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Dictionary to map doctor specialities to relevant notes
SPECIALITY_NOTES = {
    'Cardiology': 'Monitor heart rhythm and consider ECG follow-up.',
    'Dermatology': 'Assess skin lesions and recommend topical treatment.',
    'Neurology': 'Evaluate neurological symptoms and schedule MRI if needed.',
    'Orthopedics': 'Review joint mobility and consider physical therapy.',
    'Pediatrics': 'Ensure vaccinations are up-to-date and monitor growth.',
    'General Practice': 'Conduct routine health check and update medical history.',
}

@app.route('/submit_lab_report', methods=['POST'])
def submit_lab_report():
    try:
        # Check if request is JSON or form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        patient_email = data.get('patient_email')
        doctor_id = data.get('doctor_id')
        doctor_speciality = data.get('doctor_speciality')

        if not all([patient_email, doctor_id, doctor_speciality]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Derive patient name from email (e.g., extract before '@' or use a placeholder)
        patient_name = patient_email.split('@')[0].replace('.', ' ').title()

        # Generate notes based on doctor's speciality
        notes = SPECIALITY_NOTES.get(doctor_speciality, 'Routine follow-up recommended.')

        # Generate fake lab report data
        report_data = {
            'patient_name': patient_name,
            'test_date': fake.date_this_year().strftime('%Y-%m-%d'),
            'blood_pressure': f"{fake.random_int(90, 140)}/{fake.random_int(60, 90)} mmHg",
            'heart_rate': f"{fake.random_int(60, 100)} bpm",
            'glucose_level': f"{fake.random_int(70, 140)} mg/dL",
            'cholesterol': f"{fake.random_int(150, 240)} mg/dL",
            'notes': notes
        }

        # Store in database
        conn = sqlite3.connect('lab_reports.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO lab_reports (patient_email, doctor_id, doctor_speciality, report_data, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            patient_email,
            doctor_id,
            doctor_speciality,
            str(report_data),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Lab report saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_lab_reports/<patient_email>', methods=['GET'])
def get_lab_reports(patient_email):
    try:
        conn = sqlite3.connect('lab_reports.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, patient_email, doctor_id, doctor_speciality, report_data, created_at
            FROM lab_reports
            WHERE patient_email = ?
        ''', (patient_email,))
        reports = cursor.fetchall()
        conn.close()

        lab_reports = []
        for report in reports:
            lab_reports.append({
                'id': report[0],
                'patient_email': report[1],
                'doctor_id': report[2],
                'doctor_speciality': report[3],
                'report_data': eval(report[4]),  # Convert string back to dict
                'created_at': report[5]
            })

        return jsonify({'lab_reports': lab_reports}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submit_lab_report/<int:id>', methods=['DELETE'])
def delete_lab_report(id):
    try:
        conn = sqlite3.connect('lab_reports.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM lab_reports WHERE id = ?', (id,))
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Lab report not found'}), 404
        conn.commit()
        conn.close()
        return jsonify({
            'message': 'Lab report deleted successfully',
            'id': id
        }), 200
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5002, debug=True)