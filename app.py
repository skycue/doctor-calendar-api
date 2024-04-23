from flask import Flask, jsonify, request
from datetime import datetime
import uuid

app = Flask(__name__)

# Doctors data
id1 = str(uuid.uuid4())
id2 = str(uuid.uuid4())
doctors = [
    {'id': id1, 'first_name': 'Jack', 'last_name': 'Smith'},
    {'id': id2, 'first_name': 'Emily', 'last_name': 'Lee'}
]

# Starting appointments data
appointments = [
    {'id': str(uuid.uuid4()), 'doctor_id': id1, 'patient_first_name': 'June', 'patient_last_name': 'Lane', 'datetime': '2024-04-23 08:00', 'kind': 'New Patient'},
    {'id': str(uuid.uuid4()), 'doctor_id': id1, 'patient_first_name': 'Mary', 'patient_last_name': 'Jane', 'datetime': '2024-04-23 09:00', 'kind': 'Follow-up'},
    {'id': str(uuid.uuid4()), 'doctor_id': id2, 'patient_first_name': 'Crystal', 'patient_last_name': 'Lee', 'datetime': '2024-04-23 10:00', 'kind': 'New Patient'}
]

# Convert datetime string to datetime object
def str_to_datetime(datetime_str):
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

# Convert datetime object to string
def datetime_to_str(datetime_obj):
    return datetime_obj.strftime('%Y-%m-%d %H:%M')

# Get all doctors
@app.route('/doctors', methods=['GET'])
def get_doctors():
    if not doctors:
        return jsonify({'message': 'No doctors available.'}), 404
    
    return jsonify(doctors), 200

# Get all appointments for given doctor and date
@app.route('/appointments/<doctor_id>/<date>', methods=['GET'])
def get_appointments_by_doctor_and_day(doctor_id, date):
    date = date.strip()
    try:
        datetime_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400
    
    doctor_appointments = [appointment for appointment in appointments if appointment['doctor_id'] == doctor_id and str_to_datetime(appointment['datetime']).date() == datetime_obj]
    if not doctor_appointments:
        return jsonify({'error': 'No appointments found with given doctor and date.'}), 404
    
    return jsonify(doctor_appointments), 200

# Delete an appointment from a doctor's calendar
@app.route('/appointments/<appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    global appointments

    appointment = next((appointment for appointment in appointments if appointment['id'] == appointment_id), None)
    if appointment:
        appointments = [appt for appt in appointments if appt['id'] != str(appointment_id)]
        return '', 204
    else:
        return jsonify({'error': 'Appointment was not found'}), 404

# Add a new appointment to a doctor's calendar
@app.route('/appointments', methods=['POST'])
def add_appointment():
    global appointments

    data = request.json
    doctor_id = data.get('doctor_id')
    patient_first_name = data.get('patient_first_name')
    patient_last_name = data.get('patient_last_name')
    appointment_datetime = data.get('datetime')
    kind = data.get('kind')

    if not all([doctor_id, patient_first_name, patient_last_name, appointment_datetime, kind]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if kind not in ['New Patient', 'Follow-up']:
        return jsonify({'error': "Invalid appointment type. Must be 'New Patient' or 'Follow-up'."}), 400
    
    try:
        appointment_datetime = str_to_datetime(appointment_datetime)
    except ValueError:
        return jsonify({'error': 'Invalid datetime format. Please use YYYY-MM-DD HH:MM.'}), 400

    if appointment_datetime.minute % 15 != 0:
        return jsonify({'error': 'Appointment time must be in 15 minute intervals'}), 400

    doctor_appointments_same_time = [appointment for appointment in appointments if appointment['doctor_id'] == doctor_id and str_to_datetime(appointment['datetime']) == appointment_datetime]
    if len(doctor_appointments_same_time) >= 3:
        return jsonify({'error': 'This doctor already has 3 appointments at the same time'}), 400

    new_appointment = {
        'id': str(uuid.uuid4()),
        'doctor_id': doctor_id,
        'patient_first_name': patient_first_name,
        'patient_last_name': patient_last_name,
        'datetime': datetime_to_str(appointment_datetime),
        'kind': kind
    }
    appointments.append(new_appointment)

    return jsonify({'message': 'Appointment added successfully', 'appointment': new_appointment}), 201

if __name__ == '__main__':
    app.run(debug=True)
