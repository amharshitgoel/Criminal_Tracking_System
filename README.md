# 🕵️ Criminal Tracking System

A facial recognition–powered dashboard that allows law enforcement and users to search, manage, and track criminal records across jurisdictions. Built with **Streamlit**, **DeepFace**, and **OpenCV**, this lightweight web app features secure OTP-based login, role-specific access, and real-time facial matching 


## 🔥 Features

- ✅ **Face Matching via DeepFace**  
  Upload a photo and instantly search the criminal database for matches using DeepFace models (MTCNN, RetinaFace).

- 🔐 **OTP-Based Login System**  
  - Secure login via One-Time Password sent to registered email addresses.  
  - Built-in validation via `email-validator`.

- 🧑‍💼 **Role-Based Dashboards**  
  - **Admin**: full access to add/edit/delete criminal records, manage case data, and view logs.  
  - **User**: search and match records aacording to permission

- 📂 **Criminal Record Management**  
  Create, update criminal record with photos, gender, case type, jurisdiction, and status.

- 📍 **Jurisdiction & Crime Filters**  
  Search records using filters like crime type, location, gender, and case status.

- 🖼️ **Interactive Dashboard UI**  
  Sidebar-driven layout with modular components for login, search, admin panel, and case review.

- 🧠 **SQLite Backend with Pandas Interface**  
  Fast local data access and querying using lightweight embedded database.

## 🚀 Quickstart

### 1️⃣ Clone the Repository

bash
git clone https://github.com/amharshitgoel/Criminal_Tracking_System
cd Criminal_Tracking_System
