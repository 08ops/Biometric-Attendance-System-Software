from PyQt5.QtWidgets import QMainWindow, QMenu
from PyQt5.QtGui import QActionEvent
from ui_index import Ui_MainWindow


class MySideBar(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Attendance Tracker")
        self.stackedWidget.setCurrentIndex(0)

    #hide Widget Menu
        self.icon_only_widget.setHidden(True)
    
    #Connect Buttons to switch to different pages
        self.home1.clicked.connect(self.switch_to_home_page)
        self.home2.clicked.connect(self.switch_to_home_page)

        self.students1.clicked.connect(self.switch_to_studets_page)
        self.students2.clicked.connect(self.switch_to_studets_page)

        self.attendance1.clicked.connect(self.switch_to_attendance_page)
        self.attendance2.clicked.connect(self.switch_to_attendance_page)

        self.fingerprint1.clicked.connect(self.switch_to_fingerprint_page)
        self.fingerprint2.clicked.connect(self.switch_to_fingerprint_page)

    #Connect to mysql server and create database if it doesn't exist
        self.create_connection()

    #Create students table
        self.create_students_table()

    #Open add student dialog
        self.addStudent_btn.clicked.connect(self.open_addStudent_dialog)

    #Method to switch to different pages
    def switch_to_home_page(self):
        self.stackedWidget.setCurrentIndex(0)

    def switch_to_studets_page(self):
        self.stackedWidget.setCurrentIndex(1)

    def switch_to_attendance_page(self):
        self.stackedWidget.setCurrentIndex(2)

    def switch_to_fingerprint_page(self):
        self.stackedWidget.setCurrentIndex(3)

    