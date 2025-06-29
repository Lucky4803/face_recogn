import React, { useState } from 'react';
import { supabase } from '../lib/supabase';
import { Download, Share2 } from 'lucide-react';
import toast from 'react-hot-toast';
import * as XLSX from 'xlsx';

interface ExportButtonsProps {
  selectedDate: string;
}

export const ExportButtons: React.FC<ExportButtonsProps> = ({ selectedDate }) => {
  const [exporting, setExporting] = useState(false);

  const fetchAttendanceData = async () => {
    const { data, error } = await supabase
      .from('attendance')
      .select(`
        *,
        students (
          name,
          email,
          phone
        )
      `)
      .eq('date', selectedDate)
      .order('timestamp', { ascending: true });

    if (error) {
      toast.error('Failed to fetch attendance data');
      throw error;
    }

    return data || [];
  };

  const exportToExcel = async () => {
    try {
      setExporting(true);
      const data = await fetchAttendanceData();

      const worksheetData = data.map(record => ({
        'Student Name': record.students?.name || '',
        'Email': record.students?.email || '',
        'Phone': record.students?.phone || '',
        'Session Type': record.session_type.replace('_', ' '),
        'Time': new Date(record.timestamp).toLocaleTimeString(),
        'Date': record.date,
      }));

      const worksheet = XLSX.utils.json_to_sheet(worksheetData);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Attendance');

      worksheet['!cols'] = worksheetData[0]
        ? Object.keys(worksheetData[0]).map(() => ({ wch: 20 }))
        : [];

      XLSX.writeFile(workbook, `attendance-${selectedDate}.xlsx`);
      toast.success('Excel file downloaded successfully!');
    } catch (error) {
      console.error('Export error:', error);
      toast.error('Failed to export to Excel');
    } finally {
      setExporting(false);
    }
  };

  const exportToGoogleSheets = async () => {
    try {
      setExporting(true);
      const data = await fetchAttendanceData();

      const response = await fetch('http://localhost:5000/export-to-sheets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          date: selectedDate,
          records: data.map(record => ({
            student_name: record.students?.name || '',
            email: record.students?.email || '',
            phone: record.students?.phone || '',
            session_type: record.session_type,
            timestamp: record.timestamp,
            date: record.date,
          })),
        }),
      });

      if (!response.ok) {
        const errorResponse = await response.json();
        throw new Error(errorResponse.error || 'Export failed');
      }

      const result = await response.json();
      toast.success('Data exported to Google Sheets successfully!');

      if (result.spreadsheet_url) {
        window.open(result.spreadsheet_url, '_blank');
      }
    } catch (error) {
      console.error('Google Sheets export error:', error);
      toast.error('Failed to export to Google Sheets');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="flex items-center space-x-3">
      <button
        onClick={exportToExcel}
        disabled={exporting}
        className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
      >
        {exporting ? (
          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        ) : (
          <Download className="w-4 h-4" />
        )}
        <span>Excel</span>
      </button>

      <button
        onClick={exportToGoogleSheets}
        disabled={exporting}
        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
      >
        {exporting ? (
          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        ) : (
          <Share2 className="w-4 h-4" />
        )}
        <span>Google Sheets</span>
      </button>
    </div>
  );
};
