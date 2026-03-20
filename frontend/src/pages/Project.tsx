import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import apiClient from '../api/client';
import type { Project as ProjectType, Chapter } from '../types';

export default function Project() {
  const { id } = useParams<{ id: string }>();

  const [project, setProject] = useState<ProjectType | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const [projectRes, chaptersRes] = await Promise.all([
          apiClient.get<ProjectType>(`/api/projects/${id}`),
          apiClient.get<Chapter[]>(`/api/projects/${id}/chapters`),
        ]);
        setProject(projectRes.data);
        setChapters(chaptersRes.data);
      } catch {
        setError('Failed to load project');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [id]);

  if (loading) return <p className="text-gray-500">Loading...</p>;
  if (error || !project) {
    return (
      <div>
        <Link to="/" className="text-sm text-blue-600 hover:underline">&larr; Back to projects</Link>
        <p className="mt-4 text-red-600">{error || 'Project not found'}</p>
      </div>
    );
  }

  return (
    <div>
      <Link to="/" className="text-sm text-blue-600 hover:underline">&larr; Back to projects</Link>

      <div className="mt-4 mb-6">
        <h1 className="text-3xl font-bold text-gray-900">{project.title}</h1>
        {project.description && <p className="mt-1 text-gray-500">{project.description}</p>}
        <p className="mt-1 text-sm text-gray-400">
          {project.source_language} → {project.target_language}
        </p>
      </div>

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Chapters</h2>
        <div className="flex gap-3">
          <Link
            to={`/projects/${id}/upload`}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
          >
            Upload Chapter
          </Link>
          <Link
            to={`/projects/${id}/report`}
            className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            View Report
          </Link>
        </div>
      </div>

      {chapters.length === 0 ? (
        <p className="text-gray-500">No chapters uploaded yet.</p>
      ) : (
        <div className="grid gap-3">
          {chapters.map((ch) => (
            <div
              key={ch.id}
              className="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-5 py-4"
            >
              <div>
                <p className="font-medium text-gray-900">
                  Chapter {ch.chapter_number}
                  {ch.title && <span className="text-gray-500"> — {ch.title}</span>}
                </p>
                <p className="text-xs text-gray-400">
                  Uploaded {new Date(ch.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
