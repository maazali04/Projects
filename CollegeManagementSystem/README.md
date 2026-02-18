# 🏛️ Smart College Management System

A professional-grade, offline-first desktop application designed for educational institutions to manage student records and fee tracking with precision. Built with a focus on **Object-Oriented Programming (OOP)**, **Modern UI/UX**, and **Persistent Relational Storage**.

---

## 🚀 Overview
The Smart College System is more than just a CRUD application. it implements a custom business logic layer to automate financial tracking. It features a modern, responsive interface built with `CustomTkinter` and a high-performance `SQLite` backend.

### 💡 Key Features
* **Automated Fee Logic:** System-wide detection of outstanding balances (e.g., 500 PKR threshold) with dynamic UI badge updates.
* **Modern UI/UX:** A sleek "Inter" font-based interface with a professional color palette and responsive sidebar navigation.
* **Data Integrity:** Relational database management ensuring persistent student records and secure fee history.
* **Production Ready:** Fully packaged using PyInstaller and distributed via a professional Inno Setup installer.

---

## 🛠️ Technical Stack
* **Language:** Python 3.x
* **Frontend:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (High-level UI library based on Tkinter)
* **Database:** SQLite3 (Serverless, self-contained relational database)
* **Imaging:** PIL (Pillow) for dynamic asset rendering.
* **Deployment:** PyInstaller (Binary Compilation) & Inno Setup (Distribution).

---

## 🏗️ Architectural Highlights

### 1. Resource Path Resolution
To ensure cross-platform compatibility and successful binary compilation, the project utilizes a custom `resource_path` resolution algorithm to handle the `sys._MEIPASS` temporary directory used by PyInstaller.

### 2. Centralized Theme Management
The application implements a `ThemeManager` class to decouple design from logic, allowing for easy updates to typography and color schemes across the entire system.

---

## 📸 Screenshots
*(Tip: Add your app screenshots here to show off that beautiful UI!)*
| Dashboard | Fee Management |
| :---: | :---: |
| ![Dashboard Screenshot](docs/dashboard.png) | ![Fees Screenshot](docs/fees.png) |

---

## 📦 Installation
1. Download the latest `SmartCollegeSystem_Setup.exe` from the [Releases](https://github.com/maazali04/Projects/releases/tag/v1.0.0) tab.
2. Run the installer and follow the wizard.
3. Launch the application from your Desktop shortcut.

## 👨‍💻 For Developers (Local Setup)
```bash
# Clone the repository
git clone [https://github.com/maazali04/SmartCollegeSystem.git](https://github.com/maazali04/SmartCollegeSystem.git)

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
