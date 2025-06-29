/*
  # Student Attendance System Schema

  1. New Tables
    - `students`
      - `id` (uuid, primary key)
      - `name` (text, required)
      - `email` (text, unique, required)
      - `phone` (text, required)
      - `face_descriptor` (text, optional - for storing face encodings)
      - `image_url` (text, optional - URL to face photo in storage)
      - `created_at` (timestamp with timezone, default now)
    
    - `attendance`
      - `id` (uuid, primary key)
      - `student_id` (uuid, foreign key to students)
      - `session_type` (enum: 'before_break' | 'end_of_day')
      - `timestamp` (timestamp with timezone, default now)
      - `date` (date, required)
      - `created_at` (timestamp with timezone, default now)

  2. Storage
    - Create `student-photos` bucket for storing face images

  3. Security
    - Enable RLS on both tables
    - Add policies for authenticated users (admin access)
    - Create indexes for performance

  4. Functions
    - Function to prevent duplicate attendance for same day/session
*/

-- Create custom types
CREATE TYPE session_type AS ENUM ('before_break', 'end_of_day');

-- Create students table
CREATE TABLE IF NOT EXISTS students (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  email text UNIQUE NOT NULL,
  phone text NOT NULL,
  face_descriptor text,
  image_url text,
  created_at timestamptz DEFAULT now()
);

-- Create attendance table
CREATE TABLE IF NOT EXISTS attendance (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id uuid REFERENCES students(id) ON DELETE CASCADE,
  session_type session_type NOT NULL,
  timestamp timestamptz DEFAULT now(),
  date date NOT NULL DEFAULT CURRENT_DATE,
  created_at timestamptz DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);
CREATE INDEX IF NOT EXISTS idx_attendance_student_id ON attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);
CREATE INDEX IF NOT EXISTS idx_attendance_session_type ON attendance(session_type);
CREATE INDEX IF NOT EXISTS idx_attendance_date_session ON attendance(date, session_type);

-- Create unique constraint to prevent duplicate attendance
CREATE UNIQUE INDEX IF NOT EXISTS idx_attendance_unique_daily_session 
ON attendance(student_id, date, session_type);

-- Enable Row Level Security
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;

-- Create policies for students table
CREATE POLICY "Allow authenticated users to manage students"
  ON students
  FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- Create policies for attendance table
CREATE POLICY "Allow authenticated users to manage attendance"
  ON attendance
  FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- Create storage bucket for student photos
INSERT INTO storage.buckets (id, name, public)
VALUES ('student-photos', 'student-photos', true)
ON CONFLICT (id) DO NOTHING;

-- Create storage policy
CREATE POLICY "Allow authenticated users to manage student photos"
  ON storage.objects
  FOR ALL
  TO authenticated
  USING (bucket_id = 'student-photos')
  WITH CHECK (bucket_id = 'student-photos');

-- Function to get daily attendance summary
CREATE OR REPLACE FUNCTION get_daily_attendance_summary(target_date date DEFAULT CURRENT_DATE)
RETURNS TABLE (
  total_students bigint,
  before_break_count bigint,
  end_of_day_count bigint,
  total_attendance bigint
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    (SELECT COUNT(*) FROM students) as total_students,
    (SELECT COUNT(*) FROM attendance WHERE date = target_date AND session_type = 'before_break') as before_break_count,
    (SELECT COUNT(*) FROM attendance WHERE date = target_date AND session_type = 'end_of_day') as end_of_day_count,
    (SELECT COUNT(*) FROM attendance WHERE date = target_date) as total_attendance;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to prevent duplicate attendance (trigger function)
CREATE OR REPLACE FUNCTION prevent_duplicate_attendance()
RETURNS TRIGGER AS $$
BEGIN
  -- Check if attendance already exists for this student, date, and session
  IF EXISTS (
    SELECT 1 FROM attendance 
    WHERE student_id = NEW.student_id 
    AND date = NEW.date 
    AND session_type = NEW.session_type
  ) THEN
    RAISE EXCEPTION 'Attendance already marked for student % on % for %', 
      NEW.student_id, NEW.date, NEW.session_type;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to prevent duplicate attendance
DROP TRIGGER IF EXISTS trigger_prevent_duplicate_attendance ON attendance;
CREATE TRIGGER trigger_prevent_duplicate_attendance
  BEFORE INSERT ON attendance
  FOR EACH ROW
  EXECUTE FUNCTION prevent_duplicate_attendance();