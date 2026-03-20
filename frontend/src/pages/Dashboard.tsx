import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import type { Project } from '../types';

interface HealthStatus {
  backend: string;
  database: string;
  database_error: string | null;
}

export default function Dashboard() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [healthError, setHealthError] = useState<string | null>(null);

  const [projects, setProjects] = useState<Project[]>([]);
  const [projectsLoading, setProjectsLoading] = useState(true);

  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  async function fetchProjects() {
    setProjectsLoading(true);
    try {
      const res = await apiClient.get<Project[]>('/api/projects');
      setProjects(res.data);
    } catch {
      // silently fail — user can retry
    } finally {
      setProjectsLoading(false);
    }
  }

  async function checkHealth() {
    setHealthLoading(true);
    setHealthError(null);
    setHealth(null);
    try {
      const res = await apiClient.get<HealthStatus>('/health');
      setHealth(res.data);
    } catch {
      setHealthError('Cannot reach backend');
    } finally {
      setHealthLoading(false);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setCreating(true);
    setFormError(null);
    try {
      await apiClient.post('/api/projects', { title: title.trim(), description: description.trim() || null });
      setTitle('');
      setDescription('');
      setShowForm(false);
      await fetchProjects();
    } catch {
      setFormError('Failed to create project');
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this project and all its data?')) return;
    try {
      await apiClient.delete(`/api/projects/${id}`);
      await fetchProjects();
    } catch {
      // ignore
    }
  }

  return (
    <div>
      {/* Health check */}
      <div className="mb-8 rounded-lg border border-gray-200 bg-white p-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">System Status</h2>
            <p className="text-sm text-gray-500">Check if backend and database are connected</p>
          </div>
          <button
            onClick={checkHealth}
            disabled={healthLoading}
            className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50"
          >
            {healthLoading ? 'Checking...' : 'Check Backend'}
          </button>
        </div>

        {healthError && (
          <div className="mt-4 flex items-center gap-3 rounded-md bg-red-50 px-4 py-3">
            <span className="text-red-600 text-lg">&#x2717;</span>
            <div>
              <p className="text-sm font-medium text-red-800">Backend unreachable</p>
              <p className="text-sm text-red-600">{healthError}</p>
            </div>
          </div>
        )}

        {health && (
          <div className="mt-4 flex flex-col gap-3">
            <StatusRow label="Backend" status={health.backend} error={null} />
            <StatusRow label="Database" status={health.database} error={health.database_error} />
          </div>
        )}
      </div>

      {/* Projects header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
        >
          {showForm ? 'Cancel' : 'New Project'}
        </button>
      </div>

      {/* Create form */}
      {showForm && (
        <form onSubmit={handleCreate} className="mb-6 rounded-lg border border-gray-200 bg-white p-5">
          <div className="mb-4">
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
              Title
            </label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="My Manga Project"
              required
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div className="mb-4">
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description..."
              rows={2}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          {formError && <p className="mb-3 text-sm text-red-600">{formError}</p>}
          <button
            type="submit"
            disabled={creating || !title.trim()}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
          >
            {creating ? 'Creating...' : 'Create Project'}
          </button>
        </form>
      )}

      {/* Project list */}
      {projectsLoading ? (
        <p className="text-gray-500">Loading projects...</p>
      ) : projects.length === 0 ? (
        <p className="text-gray-500">No projects yet. Create one to get started.</p>
      ) : (
        <div className="grid gap-4">
          {projects.map((project) => (
            <div
              key={project.id}
              className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-5"
            >
              <Link to={`/projects/${project.id}`} className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600">
                  {project.title}
                </h3>
                {project.description && (
                  <p className="mt-1 text-sm text-gray-500 truncate">{project.description}</p>
                )}
                <p className="mt-1 text-xs text-gray-400">
                  {project.source_language} → {project.target_language} · Created{' '}
                  {new Date(project.created_at).toLocaleDateString()}
                </p>
              </Link>
              <button
                onClick={() => handleDelete(project.id)}
                className="ml-4 rounded-md px-3 py-1.5 text-sm text-red-600 hover:bg-red-50"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StatusRow({ label, status, error }: { label: string; status: string; error: string | null }) {
  const isOk = status === 'ok';
  return (
    <div className={`flex items-center gap-3 rounded-md px-4 py-3 ${isOk ? 'bg-green-50' : 'bg-red-50'}`}>
      <span className={`text-lg ${isOk ? 'text-green-600' : 'text-red-600'}`}>
        {isOk ? '\u2713' : '\u2717'}
      </span>
      <div>
        <p className={`text-sm font-medium ${isOk ? 'text-green-800' : 'text-red-800'}`}>
          {label}: {isOk ? 'Connected' : 'Error'}
        </p>
        {error && <p className="text-sm text-red-600">{error}</p>}
      </div>
    </div>
  );
}
