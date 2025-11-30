# smart-attendance-system

A digital attendance management system designed to simplify attendance tracking, eliminate proxies, and provide secure, real-time records for classes, events, or meetings. The system uses QR codes with geolocation and Wi-Fi verification to ensure authenticity.

Features

Create and manage attendance topics/events.
Generate time-limited QR codes for attendance.
Proxy-proof attendance with geolocation and Wi-Fi verification.
One-time submission per student per session.
Real-time attendance tracking and visualization for admins.
Download attendance data as CSV for records.

Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Django (Python)
- Database: SQLite
-Other Tools: QR code generation libraries, Geolocation API

Project Flow

Admin Panel
Admins (teachers, professors, or event organizers) manage attendance.
Create Event/Topic: Example: "Math 101 - 6 June Attendance".
Start Attendance: Generates a QR code valid for ~2 minutes. New codes keep generating until the admin stops attendance.
View Attendance: See all submitted student details in a table. Download CSV if needed.

Attendee Panel
Students or attendees submit attendance through secure validation.
Scan QR Code: Directs students to the attendance page.
Validation Checks:
Must be connected to the required Wi-Fi.
Must be within the QR code’s geolocation range.
Can submit only once per session.
Submit Details: Enter name and roll number, then submit.
Confirmation: Successful submission is acknowledged and updated for the admin.

Setup Instructions

Clone the repository

git clone: https://github.com/jahnavi-naishadham/smart-attendance-system.git

cd smart-attendance-system


Create virtual environment

For Linux/macOS:

python -m venv venv
source venv/bin/activate


For Windows:

python -m venv venv
venv\Scripts\activate


Install dependencies

pip install -r requirements.txt


Run migrations

python manage.py migrate


Start the server

python manage.py runserver

How It Works

Admin creates an event → starts attendance → QR code is generated.
Student scans QR code → geolocation & Wi-Fi validation → submits name & roll number.
Attendance is recorded in the database → admin can view or download CSV.
QR codes refresh automatically to prevent misuse.

Screenshots

Admin dashboard view
<img width="1919" height="912" alt="image" src="https://github.com/user-attachments/assets/6f223bd1-3599-4152-80fd-66d4544bbe58" />

QR code generation
<img width="1918" height="893" alt="image" src="https://github.com/user-attachments/assets/451fcd7a-91f1-468e-803d-e7ac916c28da" />

Student submission page
<img width="1917" height="914" alt="image" src="https://github.com/user-attachments/assets/0f806afe-893b-4ad6-8a6f-ae7c32b2e4cc" />

Attendance table with CSV download
<img width="1919" height="914" alt="image" src="https://github.com/user-attachments/assets/5cf5ecc6-29cb-4c72-9652-7eb43b78591a" />