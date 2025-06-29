import React, { useState } from 'react';
import axios from 'axios';
import { supabase } from '../lib/supabase';
import { User, Mail, Phone, Camera, Upload, X } from 'lucide-react';
import toast from 'react-hot-toast';

interface StudentRegistrationProps {
  onClose: () => void;
  onSuccess: () => void;
}

export const StudentRegistration: React.FC<StudentRegistrationProps> = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    id: '',
    name: '',
    email: '',
    phone: '',
  });

  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!imageFile) {
      toast.error('Please upload a face photo');
      return;
    }

    if (!formData.id || isNaN(Number(formData.id))) {
      toast.error('Please enter a valid numeric ID');
      return;
    }

    setLoading(true);

    try {
      // Upload to Cloudinary
      const cloudinaryUrl = 'https://api.cloudinary.com/v1_1/drivss6vy/image/upload';
      const uploadPreset = 'devops';

      const formDataImage = new FormData();
      formDataImage.append('file', imageFile);
      formDataImage.append('upload_preset', uploadPreset);

      const cloudinaryRes = await axios.post(cloudinaryUrl, formDataImage);
      const imageUrl = cloudinaryRes.data.secure_url;

      // Insert into Supabase
      const { error: insertError } = await supabase
        .from('students')
        .insert({
          id: parseInt(formData.id),
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
          image_url: imageUrl,
        });

      if (insertError) {
        toast.error(`Insert failed: ${insertError.message}`);
        return;
      }

      toast.success('Student registered successfully!');
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('[ERROR]', err.response?.data || err.message || err);
      toast.error('Unexpected error occurred. See console.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Register New Student</h2>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full">
              <X className="w-5 h-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* ID Field */}
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm font-bold">#</span>
              <input
                type="number"
                value={formData.id}
                onChange={(e) => setFormData({ ...formData, id: e.target.value })}
                placeholder="Student ID"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg"
                required
              />
            </div>

            {/* Name */}
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Full Name"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg"
                required
              />
            </div>

            {/* Email */}
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="Email"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg"
                required
              />
            </div>

            {/* Phone */}
            <div className="relative">
              <Phone className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="Phone"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg"
                required
              />
            </div>

            {/* Face Photo Upload */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">Face Photo</label>
              {imagePreview && (
                <div className="flex justify-center">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="w-32 h-32 object-cover rounded-full border-4 border-gray-200"
                  />
                </div>
              )}
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <Camera className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <label className="cursor-pointer">
                  <span className="text-sm text-gray-600">Click to upload face photo</span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    className="hidden"
                    required
                  />
                </label>
              </div>
            </div>

            {/* Buttons */}
            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    <span>Register</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
