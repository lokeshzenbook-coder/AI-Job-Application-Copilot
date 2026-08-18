import { useState, useRef } from 'react';
import { api } from '../api/client';

interface Props {
  onResumeUploaded: () => void;
}

export default function ResumeUpload({ onResumeUploaded }: Props) {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);

  async function handleUpload() {
    const file = fileRef.current?.files?.[0];
    if (!file) return;

    setUploading(true);
    setError('');
    try {
      const res = await api.uploadResume(file);
      setResult(res);
      onResumeUploaded();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Upload Resume</h3>
      <div className="flex items-center gap-3">
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.docx,.txt"
          className="text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium"
        >
          {uploading ? 'Processing...' : 'Upload & Parse'}
        </button>
      </div>
      {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
      {result && (
        <div className="mt-3 text-sm text-green-700 bg-green-50 p-3 rounded">
          Resume parsed: {result.full_name} | {result.technologies_count} technologies extracted
        </div>
      )}
    </div>
  );
}
