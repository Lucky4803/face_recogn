import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export type Database = {
  public: {
    Tables: {
      students: {
        Row: {
          id: string;
          name: string;
          email: string;
          phone: string;
          face_descriptor: string | null;
          image_url: string | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          email: string;
          phone: string;
          face_descriptor?: string | null;
          image_url?: string | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          name?: string;
          email?: string;
          phone?: string;
          face_descriptor?: string | null;
          image_url?: string | null;
          created_at?: string;
        };
      };
      attendance: {
        Row: {
          id: string;
          student_id: string;
          session_type: 'before_break' | 'end_of_day';
          timestamp: string;
          date: string;
          created_at: string;
        };
        Insert: {
          id?: string;
          student_id: string;
          session_type: 'before_break' | 'end_of_day';
          timestamp?: string;
          date: string;
          created_at?: string;
        };
        Update: {
          id?: string;
          student_id?: string;
          session_type?: 'before_break' | 'end_of_day';
          timestamp?: string;
          date?: string;
          created_at?: string;
        };
      };
    };
  };
};