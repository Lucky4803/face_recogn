# 🎓 Student Attendance System with Face Recognition  
> A complete smart attendance solution built with React, Flask, Supabase & Google Sheets  
> **By [Lucky Kumar Swain](https://github.com/Lucky4803)**

---

## 🚀 Overview

A powerful and modern **Student Attendance Management System** that leverages **AI-based face recognition**, real-time updates, and seamless data exports. Designed for ease of use by administrators, this system automates the attendance process and integrates beautifully with Google Sheets and Supabase.

---

## ✨ Key Features

### 🖥️ Frontend (React + Tailwind CSS)
- 🔐 **Admin Authentication** – Secure login via Supabase Auth
- 📊 **Responsive Dashboard** – Real-time statistics and clean UI
- 🧑‍🎓 **Student Management** – Register students with face images
- 📆 **Attendance Tracking** – Mark two sessions: `before_break` & `end_of_day`
- 📤 **Data Export** – One-click export to Excel and Google Sheets
- 🔄 **Live Updates** – Auto-refresh attendance records

### 🧠 Backend (Python + Flask)
- 📸 **Face Recognition** – Real-time detection with OpenCV & `face_recognition`
- ✅ **Auto Attendance** – Smart detection and time-based logging
- 🛡️ **Duplicate Prevention** – Prevents multiple logs for the same session
- 📤 **Google Sheets Export** – Integrate with Sheets via service account
- 🧩 **RESTful APIs** – Clean and secure API endpoints

### 🛢️ Database (Supabase)
- 🐘 **PostgreSQL** – With Row-Level Security (RLS)
- 🗃️ **File Storage** – Store face images securely
- 🔔 **Real-Time Subscriptions** – Updates reflect instantly
- 💾 **Backups & Scaling** – Cloud-hosted and production-ready

---

## ⚙️ Quick Start

### 🧾 Prerequisites
- Node.js ≥ 18
- Python ≥ 3.8
- Supabase account
- Google Cloud project
- A webcam 📷

---

### 📦 1. Frontend Setup

```bash
# Install dependencies
npm install

# Create and configure env
cp .env.example .env
# Add:
# VITE_SUPABASE_URL=your_url
# VITE_SUPABASE_ANON_KEY=your_key

# Start app
npm run dev
