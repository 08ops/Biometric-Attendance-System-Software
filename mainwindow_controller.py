import sys
import serial
import sqlite3
from datetime import datetime
from PyQt5 import QtWidgets, QtCore
from index import Ui_MainWindow
from studentdialog_controller import StudentDialog
import pandas as pd
from PyQt5.QtWidgets import QFileDialog

# Background thread to listen to Arduino
class AttendanceListener(QtCore.QThread):
    attendance_received = QtCore.pyqtSignal(str)

    def __init__(self, serial_port):
        super().__init__()
        self.serial = serial_port
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            if self.serial.in_waiting:
                raw_line = self.serial.readline()
                try:
                    line = raw_line.decode(errors='ignore').strip()
                    if line:
                        print("Arduino:", line)
                        if line.startswith("MATCH:"):
                            student_id = line.split(":")[1]
                            self.attendance_received.emit(student_id)
                except Exception as e:
                    print("Decode error:", raw_line, e)

    def stop(self):
        self.running = False
        self.wait()


class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        try:
            self.serial = serial.Serial('COM9', 9600, timeout=2)
        except Exception as e:
            print("Serial connection failed:", e)
            self.serial = None

        self.attendance_thread = None

        self.ui.home1.toggled.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.home2.toggled.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.students1.toggled.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.students2.toggled.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.attendance1.toggled.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.attendance2.toggled.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))

        self.ui.addStudent_btn.clicked.connect(self.open_add_student_dialog)
        self.ui.pushButton_2.clicked.connect(self.start_attendance_mode)
        self.ui.pushButton_3.clicked.connect(self.stop_attendance_mode)

        self.ui.excelExport_btn.clicked.connect(self.export_students_to_excel)
        self.ui.excelExport2_btn.clicked.connect(self.export_attendance_to_excel)

        self.load_all_students()

    def open_add_student_dialog(self):
        if self.serial:
            dialog = StudentDialog(self.serial, self)
            dialog.exec_()
            self.load_all_students()
        else:
            QtWidgets.QMessageBox.critical(self, "Serial Error", "Arduino not connected.")

    def load_all_students(self):
        self.ui.studentinfo_table.setRowCount(0)
        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, gender, class, department, dob, phone FROM students")
        for row_data in cursor.fetchall():
            row = self.ui.studentinfo_table.rowCount()
            self.ui.studentinfo_table.insertRow(row)
            for col, item in enumerate(row_data):
                self.ui.studentinfo_table.setItem(row, col, QtWidgets.QTableWidgetItem(str(item)))
        conn.close()

    def start_attendance_mode(self):
        if not self.serial:
            QtWidgets.QMessageBox.warning(self, "Error", "Arduino not connected.")
            return

        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

        self.attendance_thread = AttendanceListener(self.serial)
        self.attendance_thread.attendance_received.connect(self.mark_attendance)
        self.attendance_thread.start()
        self.serial.write(b'ATTEND\n')
        print("Attendance mode started.")
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

    def stop_attendance_mode(self):
        if self.attendance_thread:
            self.attendance_thread.stop()
            self.attendance_thread = None
            print("Attendance mode stopped.")
            QtWidgets.QMessageBox.information(self, "Session Ended", "Attendance session has been ended.")

        if self.serial and self.serial.is_open:
            try:
                self.serial.reset_input_buffer()
                self.serial.reset_output_buffer()
                self.serial.write(b'END_ATTEND\n')
                self.serial.flush()
                QtCore.QThread.msleep(100)
                self.serial.reset_input_buffer()
                print("Sent END_ATTEND to Arduino and cleared buffer.")
            except Exception as e:
                print("Failed to send END_ATTEND to Arduino:", e)

    def mark_attendance(self, student_id):
        try:
            print("Received ID from Arduino:", student_id)
            conn = sqlite3.connect("students.db")
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    student_id TEXT,
                    name TEXT,
                    gender TEXT,
                    class TEXT,
                    department TEXT,
                    date TEXT,
                    time TEXT
                )
            """)

            cursor.execute("SELECT name, gender, class, department FROM students WHERE id=?", (student_id,))
            result = cursor.fetchone()

            if result:
                name, gender, class_, department = result
                now = datetime.now()
                date = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:%M:%S")

                cursor.execute("""
                    INSERT INTO attendance (student_id, name, gender, class, department, date, time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (student_id, name, gender, class_, department, date, time_str))

                conn.commit()

                row = self.ui.attendance_table.rowCount()
                self.ui.attendance_table.insertRow(row)
                self.ui.attendance_table.setItem(row, 0, QtWidgets.QTableWidgetItem(student_id))
                self.ui.attendance_table.setItem(row, 1, QtWidgets.QTableWidgetItem(name))
                self.ui.attendance_table.setItem(row, 2, QtWidgets.QTableWidgetItem(gender))
                self.ui.attendance_table.setItem(row, 3, QtWidgets.QTableWidgetItem(class_))
                self.ui.attendance_table.setItem(row, 4, QtWidgets.QTableWidgetItem(department))
                self.ui.attendance_table.setItem(row, 5, QtWidgets.QTableWidgetItem(date))
                self.ui.attendance_table.setItem(row, 6, QtWidgets.QTableWidgetItem(time_str))
            else:
                QtWidgets.QMessageBox.warning(self, "Unknown ID", f"No student found with ID {student_id}")
        except Exception as e:
            print("Error in mark_attendance:", e)
        finally:
            conn.close()

    def end_session_and_close(self):
        self.stop_attendance_mode()
        self.close()

    def export_students_to_excel(self):
        try:
            conn = sqlite3.connect("students.db")
            df = pd.read_sql_query("SELECT * FROM students", conn)
            conn.close()

            file_path, _ = QFileDialog.getSaveFileName(self, "Save Student List", "", "Excel Files (*.xlsx)")
            if file_path:
                df.to_excel(file_path, index=False)
                QtWidgets.QMessageBox.information(self, "Export Successful", f"Student list saved to:\n{file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export Failed", str(e))

    def export_attendance_to_excel(self):
        try:
            conn = sqlite3.connect("students.db")
            df = pd.read_sql_query("SELECT * FROM attendance", conn)
            conn.close()

            file_path, _ = QFileDialog.getSaveFileName(self, "Save Attendance Sheet", "", "Excel Files (*.xlsx)")
            if file_path:
                df.to_excel(file_path, index=False)
                QtWidgets.QMessageBox.information(self, "Export Successful", f"Attendance sheet saved to:\n{file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export Failed", str(e))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
