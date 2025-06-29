import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { Clock, User, Coffee, Moon, Search } from 'lucide-react';
import { format } from 'date-fns';

interface AttendanceRecord {
  id: string;
  student_id: string;
  session_type: 'before_break' | 'end_of_day';
  timestamp: string;
  date: string;
  students: {
    name: string;
    email: string;
  };
}

interface AttendanceTableProps {
  selectedDate: string;
}

export const AttendanceTable: React.FC<AttendanceTableProps> = ({ selectedDate }) => {
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchAttendance = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('attendance')
        .select(`
          *,
          students (
            name,
            email
          )
        `)
        .eq('date', selectedDate)
        .order('timestamp', { ascending: false });

      if (error) throw error;
      setRecords(data || []);
    } catch (error) {
      console.error('Error fetching attendance:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAttendance();
  }, [selectedDate]);

  const filteredRecords = records.filter(record =>
    record.students?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    record.students?.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getSessionIcon = (sessionType: string) => {
    return sessionType === 'before_break' ? Coffee : Moon;
  };

  const getSessionColor = (sessionType: string) => {
    return sessionType === 'before_break' 
      ? 'bg-green-100 text-green-800' 
      : 'bg-purple-100 text-purple-800';
  };

  if (loading) {
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">
            Attendance Records - {format(new Date(selectedDate), 'MMMM d, yyyy')}
          </h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search students..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {filteredRecords.length === 0 ? (
          <div className="text-center py-12">
            <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No attendance records found for this date</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Student</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Session</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Time</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Date</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((record) => {
                  const SessionIcon = getSessionIcon(record.session_type);
                  return (
                    <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                      <td className="py-4 px-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                            <User className="w-4 h-4 text-white" />
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{record.students?.name}</p>
                            <p className="text-sm text-gray-500">{record.students?.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${getSessionColor(record.session_type)}`}>
                          <SessionIcon className="w-4 h-4" />
                          <span>{record.session_type.replace('_', ' ')}</span>
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center space-x-2">
                          <Clock className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-700">
                            {format(new Date(record.timestamp), 'h:mm a')}
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-gray-700">
                        {format(new Date(record.date), 'MMM d, yyyy')}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};