import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';

interface Recognized {
  name: string;
  image_url: string;
  status: string;
}

export const CameraPage: React.FC = () => {
  const [recognized, setRecognized] = useState<Recognized>({
    name: '',
    image_url: '',
    status: 'Waiting for recognition...'
  });

  const fetchRecognition = async () => {
    const res = await fetch('http://localhost:5000/current');
    const data = await res.json();
    if (data.name !== recognized.name) {
      setRecognized(data);
      if (data.status.includes('marked')) {
        toast.success(`${data.name}: ${data.status}`);
      } else if (data.status.includes('already')) {
        toast(`${data.name}: ${data.status}`, { icon: 'ℹ️' });
      }
    }
  };

  const handleNext = async () => {
    await fetch('http://localhost:5000/reset');
    setRecognized({
      name: '',
      image_url: '',
      status: 'Ready for next student...'
    });
  };

  useEffect(() => {
    const interval = setInterval(fetchRecognition, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-100 flex flex-col items-center p-8">
      <h1 className="text-3xl font-bold mb-4">📷 Live Face Recognition</h1>
      <img
        src="http://localhost:5000/video_feed"
        alt="Live Feed"
        className="rounded-xl shadow-lg border"
        width={480}
      />
      <div className="mt-6 p-6 bg-white shadow-xl rounded-lg text-center max-w-md w-full">
        <h2 className="text-2xl font-semibold mb-2">{recognized.name || 'No one detected yet'}</h2>
        {recognized.image_url && (
          <img
            src={recognized.image_url}
            alt="Recognized"
            className="w-24 h-24 rounded-full mx-auto mb-2 border-2 border-blue-400"
          />
        )}
        <p className="text-gray-600">{recognized.status}</p>
        <button
          onClick={handleNext}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
        >
          Next Student
        </button>
      </div>
    </div>
  );
};
