# 🔐 Fingerprint-Based Biometric Attendance System

A complete biometric attendance system built using Arduino and Python. This project allows institutions to record and manage student attendance using fingerprint verification, real-time PC communication, and a user-friendly GUI.

## 📦 Project Components

### 🔧 Hardware
- Arduino Uno
- Fingerprint Sensor (R305/GT-521F52 or similar)
- I2C 16x2 LCD Display (address `0x27`)
- HC-05 Bluetooth module *(if using Bluetooth)*
- Buzzer
- Red, Green, and Blue LEDs
- Real-Time Clock (RTC) Module
- Power supply (USB or external)

### 🖥️ Software (Python + PyQt5 GUI)
- Student Profile Management (Name, ID, Course, Circular Photo)
- Fingerprint Registration & Matching
- Class Management (Group students)
- Real-Time Attendance Logging
- USB Serial Communication with Arduino
- Attendance Export to Excel (.xlsx)
- Attendance Percentage Tracking

## 🖼️ GUI Features

- **Dashboard**: Launch attendance sessions, view reports.
- **Student Manager**: Add, edit, and delete profiles with fingerprint registration.
- **Class Manager**: Create classes and assign students.
- **Live Attendance**: Start/stop sessions and log attendance via fingerprint recognition.
- **Export**: Save records to Excel.
- **Statistics**: Track attendance percentage for each student per class.

## 📂 Project Structure
Fingerprint-Attendance-System/

├── arduino/                       
│   ├── fingerprint_attendance.ino 
│   └── libraries/                
│
├── software/                      
│   ├── main.py                    
│   ├── serial_comm.py            
│   ├── fingerprint_manager.py     
│   ├── attendance_manager.py     
│   ├── class_manager.py         
│   ├── student_manager.py       
│   ├── excel_exporter.py  
│   ├── ui/  
│   │  ├── main_window.ui
│   │   ├── student_editor.ui
│   │   └── ...
│   ├── assets/                    
│   │   ├── photos/                
│   │   └── icons/
│   ├── database/  
│   │   ├── students.db
│   │   └── config.json
│   └── utils/                    
│       ├── image_utils.py
│       └── percentage_tracker.py
│
├── requirements.txt               
├── README.md                    
└── LICENSE                     
