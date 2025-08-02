from PyQt5.QtWidgets import QDialog, QMessageBox
import sqlite3
import time
from studentdialog import Ui_StudentDialog

class StudentDialog(QDialog):
    def __init__(self, serial_connection, parent=None):
        super().__init__(parent)
        self.ui = Ui_StudentDialog()
        self.ui.setupUi(self)

        self.arduino = serial_connection

        # Setup database
        self.conn = sqlite3.connect("students.db")
        self.create_table()

        # Connect fingerprint button
        self.ui.saveStudent_btn_2.clicked.connect(self.enroll_fingerprint)

    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT,
                gender TEXT,
                class TEXT,
                dob TEXT,
                department TEXT,
                phone TEXT,
                email TEXT
            )
        """)
        self.conn.commit()

    def enroll_fingerprint(self):
        # Collect data from UI
        name = self.ui.name_lineEdit.text()
        gender = self.ui.gender_comboBox.currentText()
        student_class = self.ui.class_comboBox.currentText()
        dob = self.ui.dob_dateEdit.date().toString("yyyy-MM-dd")
        department = self.ui.department_comboBox.currentText()
        phone = self.ui.phone_lineEdit.text()
        email = self.ui.email_lineEdit.text()
        student_id = self.ui.email_lineEdit.text()  # Must be a numeric ID between 1-127

        # Validation
        if not name or not student_id.isdigit():
            QMessageBox.warning(self, "Input Error", "Enter a valid name and numeric student ID.")
            return

        id_num = int(student_id)
        if id_num < 1 or id_num > 127:
            QMessageBox.warning(self, "Input Error", "Fingerprint ID must be between 1 and 127.")
            return

        try:
            self.arduino.write(f"ENROLL:{id_num}\n".encode())
            QMessageBox.information(self, "Enrollment", "Place your finger on the sensor...")

            # Wait for Arduino response
            while True:
                if self.arduino.in_waiting:
                    response = self.arduino.readline().decode().strip()
                    print("Arduino:", response)
                    if response == "ENROLL_SUCCESS":
                        self.save_to_db(student_id, name, gender, student_class, dob, department, phone, email)
                        QMessageBox.information(self, "Success", "Enrollment complete!")
                        break
                    elif response == "ENROLL_FAILED":
                        QMessageBox.critical(self, "Failure", "Enrollment failed.")
                        break
        except Exception as e:
            QMessageBox.critical(self, "Serial Error", str(e))

    def save_to_db(self, student_id, name, gender, student_class, dob, department, phone, email):
        self.conn.execute("""
            INSERT OR REPLACE INTO students (id, name, gender, class, dob, department, phone, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (student_id, name, gender, student_class, dob, department, phone, email))
        self.conn.commit()
