# Student Attendance System with Face Recognition

A comprehensive student attendance management system featuring automated face recognition, real-time tracking, and seamless data export capabilities.

## 🌟 Features

### Frontend (React + Tailwind CSS)
- **Admin Authentication**: Secure login system with Supabase Auth
- **Beautiful Dashboard**: Modern, responsive admin interface with real-time statistics
- **Student Management**: Register students with face photos
- **Attendance Tracking**: Monitor attendance for two daily sessions (before_break, end_of_day)
- **Data Export**: Export to Excel and Google Sheets with one click
- **Real-time Updates**: Live attendance monitoring with auto-refresh

### Backend (Python + Flask)
- **Face Recognition**: Advanced face detection using OpenCV and face_recognition library
- **Automated Attendance**: Mark attendance automatically when faces are recognized
- **Duplicate Prevention**: Smart logic to prevent duplicate attendance marking
- **Google Sheets Integration**: Direct export to Google Sheets with service account authentication
- **RESTful API**: Clean API endpoints for frontend integration

### Database (Supabase)
- **PostgreSQL**: Robust relational database with RLS (Row Level Security)
- **File Storage**: Secure storage for student face photos
- **Real-time Subscriptions**: Live updates for attendance changes
- **Backup & Scaling**: Enterprise-grade database with automatic backups

## 🚀 Quick Start

### Prerequisites
- Node.js (v18 or higher)
- Python 3.8+
- Supabase account
- Webcam for face recognition
- Google Cloud account (for Sheets integration)

### 1. Frontend Setup

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Add your Supabase credentials to .env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Start development server
npm run dev
```

### 2. Database Setup

1. Create a new Supabase project
2. Run the migration file in the SQL editor:
   ```sql
   -- Copy and paste the contents of supabase/migrations/create_attendance_system.sql
   ```
3. Create the admin user:
   ```sql
   -- In Supabase Auth, create user with:
   -- Email: admin@devops.com
   -- Password: admin123
   ```

### 3. Backend Setup

```bash
# Navigate to server directory
cd server

# Install Python dependencies
pip install -r requirements.txt

# Or run the setup script
python setup.py

# Create environment file
cp .env.example .env

# Add your credentials to .env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_key
GOOGLE_SHEETS_ID=your_google_sheets_id

# Start the server
python app.py
```

### 4. Google Sheets Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API
4. Create a service account
5. Download the credentials JSON file as `credentials.json` in the server directory
6. Create a Google Sheets document and note the ID
7. Share the sheet with your service account email

## 📖 Usage

### Admin Dashboard
1. Login with `admin@devops.com` / `admin123`
2. View real-time attendance statistics
3. Register new students with face photos
4. Monitor daily attendance records
5. Export data to Excel or Google Sheets

### Face Recognition
1. Click "Start Recognition" in the dashboard
2. System will load all student faces from the database
3. Students can now approach the camera for automatic attendance
4. Attendance is marked based on time of day:
   - Before 12:00 PM: `before_break` session
   - After 12:00 PM: `end_of_day` session

### Data Export
- **Excel Export**: Downloads `.xlsx` file with attendance data
- **Google Sheets Export**: Creates a new sheet tab with date as name

## 🏗️ Architecture

### Database Schema

```sql
-- Students table
students (
  id uuid PRIMARY KEY,
  name text NOT NULL,
  email text UNIQUE NOT NULL,
  phone text NOT NULL,
  face_descriptor text,
  image_url text,
  created_at timestamptz
)

-- Attendance table
attendance (
  id uuid PRIMARY KEY,
  student_id uuid REFERENCES students(id),
  session_type enum('before_break', 'end_of_day'),
  timestamp timestamptz,
  date date,
  created_at timestamptz
)
```

### API Endpoints

- `POST /load-faces` - Load student faces into memory
- `POST /toggle-recognition` - Start/stop face recognition
- `POST /export-to-sheets` - Export data to Google Sheets
- `GET /health` - Health check endpoint

## 🔧 Configuration

### Environment Variables

**Frontend (.env)**
```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Backend (server/.env)**
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
GOOGLE_SHEETS_ID=your_google_sheets_document_id
```

### Customization

- **Session Times**: Modify the time logic in `server/app.py` line 85
- **Recognition Threshold**: Adjust tolerance in `server/app.py` line 123
- **UI Theme**: Update colors in `tailwind.config.js`
- **Face Recognition Model**: The system uses the `face_recognition` library which provides excellent accuracy

## 🛡️ Security Features

- **Row Level Security**: Database access controlled by Supabase RLS
- **Admin Authentication**: Secure login with session management
- **File Upload Security**: Validated file types and sizes
- **API Security**: CORS protection and input validation
- **Duplicate Prevention**: Database constraints prevent duplicate attendance

## 📱 Responsive Design

The interface is fully responsive and works on:
- Desktop computers (primary admin interface)
- Tablets (secondary admin access)
- Mobile devices (view-only for quick checks)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Camera not working**
- Ensure camera permissions are granted
- Check if another application is using the camera
- Verify OpenCV installation

**Face recognition not accurate**
- Ensure good lighting conditions
- Use clear, front-facing photos for registration
- Adjust recognition threshold in server code

**Database connection issues**
- Verify Supabase credentials
- Check internet connection
- Ensure RLS policies are correctly set

**Google Sheets export fails**
- Verify service account credentials
- Check if Sheets API is enabled
- Ensure proper sharing permissions

### Support

For additional support:
1. Check the troubleshooting section above
2. Review the server logs for error messages
3. Ensure all dependencies are properly installed
4. Verify environment variables are correctly set

## 🎯 Future Enhancements

- Mobile app for students
- Email notifications for attendance
- Advanced analytics and reporting
- Integration with learning management systems
- Support for multiple cameras
- Bulk student import from CSV
- Attendance history visualization