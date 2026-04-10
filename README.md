# Interview Tracker 📋

A comprehensive desktop application built with **Python** and **CustomTkinter** designed to streamline recruitment. This tool manages candidate profiles, conducts interviews with project-specific forms, and exports professional summaries.

## 🚀 Key Features

### 👤 User Management
* **Secure Authentication:** Includes Login, Registration, and Password Reset frames with password hashing.
* **Role Based Access:** Features a built in Admin mode for system-wide statistics and record management.
* **Profile Customization:** Users can update personal details and upload profile photos.

### 📝 Interview Management
* **Dynamic Sheets:** Supports project specific question sets for Aquatica, Green Leaders, Global Classroom, On The Map, and Rooted.
* **Media Integration:** Allows uploading candidate photos and attaching CVs (PDF/Word) directly to records.
* **Database Persistence:** Automatically handles MySQL table creation and stores long-text interview summaries.

### 📄 Professional Exports
* **PDF Export:** Generates summaries with candidate photos and appends existing PDF CVs.
* **Word Export:** Creates editable `.docx` files featuring the interview data and imagery.

---

## 🛠️ Tech Stack

* **GUI:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for a modern, responsive UI.
* **Database:** [MySQL](https://www.mysql.com/) via `mysql-connector-python`.
* **Imaging:** `Pillow` for profile and candidate photo processing.
* **Documents:** `python-docx` for Word and `ReportLab`/`pypdf` for PDF generation.

---

## ⚙️ Setup and Installation

### 1. Database Configuration
The app connects to a MySQL database named `user_db` on `localhost`.
1. Ensure MySQL is running.
2. Tables (`users` and `interviews`) are created automatically on the first run.
