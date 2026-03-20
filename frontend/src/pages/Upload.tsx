import { useCallback, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import apiClient from '../api/client';
import type { ChapterUpload } from '../types';

interface Preview {
  chapter_number: number;
  title: string | null;
  page_count: number;
  total_panels: number;
}

export default function Upload() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [chapterData, setChapterData] = useState<ChapterUpload | null>(null);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  function processFile(file: File) {
    setParseError(null);
    setUploadError(null);
    setChapterData(null);
    setPreview(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target?.result as string) as ChapterUpload;

        // Basic validation
        if (typeof json.chapter_number !== 'number' || json.chapter_number <= 0) {
          setParseError('chapter_number must be a positive number');
          return;
        }
        if (!Array.isArray(json.pages) || json.pages.length === 0) {
          setParseError('pages must be a non-empty array');
          return;
        }

        let totalPanels = 0;
        for (const page of json.pages) {
          if (!Array.isArray(page.panels)) {
            setParseError(`Page ${page.page_number}: panels must be an array`);
            return;
          }
          totalPanels += page.panels.length;
        }

        setChapterData(json);
        setPreview({
          chapter_number: json.chapter_number,
          title: json.title ?? null,
          page_count: json.pages.length,
          total_panels: totalPanels,
        });
      } catch {
        setParseError('Invalid JSON file');
      }
    };
    reader.readAsText(file);
  }

  function handleFileInput(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  }, []);

  async function handleUpload() {
    if (!chapterData || !id) return;
    setUploading(true);
    setUploadError(null);
    try {
      await apiClient.post(`/api/projects/${id}/chapters`, chapterData);
      navigate(`/projects/${id}`);
    } catch (err: unknown) {
      if (
        typeof err === 'object' &&
        err !== null &&
        'response' in err &&
        typeof (err as Record<string, unknown>).response === 'object'
      ) {
        const response = (err as { response: { status: number; data?: { detail?: string } } }).response;
        if (response.status === 409) {
          setUploadError(response.data?.detail || 'Duplicate chapter number');
        } else if (response.status === 422) {
          setUploadError('Validation error — check your JSON structure');
        } else {
          setUploadError('Upload failed');
        }
      } else {
        setUploadError('Upload failed');
      }
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <Link to={`/projects/${id}`} className="text-sm text-blue-600 hover:underline">
        &larr; Back to project
      </Link>

      <h1 className="mt-4 text-3xl font-bold text-gray-900 mb-6">Upload Chapter</h1>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`mb-6 flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-10 transition-colors ${
          dragging ? 'border-blue-400 bg-blue-50' : 'border-gray-300 bg-white'
        }`}
      >
        <p className="text-gray-500 mb-3">Drag & drop a chapter JSON file here, or</p>
        <label className="cursor-pointer rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500">
          Browse Files
          <input type="file" accept=".json" onChange={handleFileInput} className="hidden" />
        </label>
      </div>

      {parseError && (
        <div className="mb-6 rounded-md bg-red-50 px-4 py-3">
          <p className="text-sm text-red-800 font-medium">Parse Error</p>
          <p className="text-sm text-red-600">{parseError}</p>
        </div>
      )}

      {/* Preview */}
      {preview && (
        <div className="mb-6 rounded-lg border border-gray-200 bg-white p-5">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Preview</h2>
          <dl className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-gray-500">Chapter Number</dt>
              <dd className="font-medium text-gray-900">{preview.chapter_number}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Title</dt>
              <dd className="font-medium text-gray-900">{preview.title || '—'}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Pages</dt>
              <dd className="font-medium text-gray-900">{preview.page_count}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Total Panels</dt>
              <dd className="font-medium text-gray-900">{preview.total_panels}</dd>
            </div>
          </dl>

          {uploadError && (
            <div className="mt-4 rounded-md bg-red-50 px-4 py-3">
              <p className="text-sm text-red-600">{uploadError}</p>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={uploading}
            className="mt-4 rounded-md bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
      )}
    </div>
  );
}
