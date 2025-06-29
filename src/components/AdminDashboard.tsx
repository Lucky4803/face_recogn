import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { StudentRegistration } from './StudentRegistration';
import { AttendanceTable } from './AttendanceTable';
import { ExportButtons } from './ExportButtons';
import { 
  Users, 
  Clock, 
  Calendar,
  UserPlus,
  LogOut,
  Coffee,
  Moon,
  TrendingUp,
  Activity,
  Eye
} from 'lucide-react';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import { CameraPage } from './CameraPage';

interface DashboardStats {
  totalStudents: number;
  presentBeforeBreak: number;
  presentEndOfDay: number;
  todayAttendance: number;
}

interface AdminDashboardProps {
  onLogout: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ onLogout }) => {
  const [stats, setStats] = useState<DashboardStats>({
    totalStudents: 0,
    presentBeforeBreak: 0,
    presentEndOfDay: 0,
    todayAttendance: 0,
  });
  const [showRegistration, setShowRegistration] = useState(false);
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [loading, setLoading] = useState(true);
  const [recognitionActive, setRecognitionActive] = useState(false);

  const fetchStats = async () => {
    try {
      const today = format(new Date(), 'yyyy-MM-dd');
      
      // Get total students
      const { count: totalStudents } = await supabase
        .from('students')
        .select('*', { count: 'exact', head: true });

      // Get today's attendance by session type
      const { data: todayAttendance } = await supabase
        .from('attendance')
        .select('session_type')
        .eq('date', today);

      const presentBeforeBreak = todayAttendance?.filter(a => a.session_type === 'before_break').length || 0;
      const presentEndOfDay = todayAttendance?.filter(a => a.session_type === 'end_of_day').length || 0;

      setStats({
        totalStudents: totalStudents || 0,
        presentBeforeBreak,
        presentEndOfDay,
        todayAttendance: todayAttendance?.length || 0,
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
      toast.error('Failed to load dashboard stats');
    } finally {
      setLoading(false);
    }
  };

const toggleRecognition = async () => {
  // Open camera tab immediately on click
  if (!recognitionActive) {
    window.open('http://localhost:5000/camera', '_blank');
  }

  try {
    const response = await fetch('http://localhost:5000/toggle-recognition', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    if (response.ok) {
      const data = await response.json();
      setRecognitionActive(data.active);
      toast.success(data.active ? 'Face recognition started' : 'Face recognition stopped');
    } else {
      throw new Error('Failed to toggle recognition');
    }
  } catch (error) {
    toast.error('Failed to communicate with recognition service');
  }
};



  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const StatCard = ({ title, value, icon: Icon, color, subtitle }: {
    title: string;
    value: number;
    icon: React.ComponentType<any>;
    color: string;
    subtitle?: string;
  }) => (
    <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-6 hover:shadow-xl transition-all duration-300">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-100">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <p className="text-gray-600 mt-1">Student Attendance Management System</p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={toggleRecognition}
              className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                recognitionActive 
                  ? 'bg-red-500 hover:bg-red-600 text-white' 
                  : 'bg-green-500 hover:bg-green-600 text-white'
              }`}
            >
              <Eye className="w-4 h-4" />
              <span>{recognitionActive ? 'Stop Recognition' : 'Start Recognition'}</span>
            </button>
            <button
              onClick={() => setShowRegistration(true)}
              className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 flex items-center space-x-2"
            >
              <UserPlus className="w-4 h-4" />
              <span>Add Student</span>
            </button>
            <button
              onClick={onLogout}
              className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Students"
            value={stats.totalStudents}
            icon={Users}
            color="bg-gradient-to-r from-blue-500 to-blue-600"
            subtitle="Registered"
          />
          <StatCard
            title="Before Break"
            value={stats.presentBeforeBreak}
            icon={Coffee}
            color="bg-gradient-to-r from-green-500 to-green-600"
            subtitle="Present today"
          />
          <StatCard
            title="End of Day"
            value={stats.presentEndOfDay}
            icon={Moon}
            color="bg-gradient-to-r from-purple-500 to-purple-600"
            subtitle="Present today"
          />
          <StatCard
            title="Today's Total"
            value={stats.todayAttendance}
            icon={TrendingUp}
            color="bg-gradient-to-r from-orange-500 to-orange-600"
            subtitle="Attendance records"
          />
        </div>

        {/* Controls */}
        <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-6 mb-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Calendar className="w-5 h-5 text-gray-500" />
                <label className="text-sm font-medium text-gray-700">Select Date:</label>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <ExportButtons selectedDate={selectedDate} />
          </div>
        </div>

        {/* Attendance Table */}
        <AttendanceTable selectedDate={selectedDate} />
      </div>

      {showRegistration && (
        <StudentRegistration
          onClose={() => setShowRegistration(false)}
          onSuccess={fetchStats}
        />
      )}
    </div>
  );
};