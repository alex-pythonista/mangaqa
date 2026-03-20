import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import apiClient from '../api/client';
import type { Project as ProjectType, Chapter, JobResponse } from '../types';

export default function Project() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<ProjectType | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [latestJob, setLatestJob] = useState<JobResponse | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const [projectRes, chaptersRes, jobsRes] = await Promise.all([
          apiClient.get<ProjectType>(`/api/projects/${id}`),
          apiClient.get<Chapter[]>(`/api/projects/${id}/chapters`),
          apiClient.get<JobResponse[]>(`/api/projects/${id}/jobs`),
        ]);
        setProject(projectRes.data);
        setChapters(chaptersRes.data);
        if (jobsRes.data.length > 0) {
          setLatestJob(jobsRes.data[0]);
        }
      } catch {
        setError('Failed to load project');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [id]);

  // Poll for job status
  useEffect(() => {
    if (!latestJob || !id) return;
    if (latestJob.status !== 'pending' && latestJob.status !== 'running') return;

    const interval = setInterval(async () => {
      try {
        const res = await apiClient.get<JobResponse>(`/api/projects/${id}/jobs/${latestJob.id}`);
        setLatestJob(res.data);
        if (res.data.status === 'completed') {
          clearInterval(interval);
          navigate(`/projects/${id}/report`);
        }
        if (res.data.status === 'failed') {
          clearInterval(interval);
        }
      } catch {
        clearInterval(interval);
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [latestJob?.id, latestJob?.status, id, navigate]);

  async function handleAnalyze() {
    if (!id) return;
    setAnalyzing(true);
    setAnalyzeError(null);
    try {
      const res = await apiClient.post<{ job_id: string; status: string }>(`/api/projects/${id}/jobs/analyze`);
      setLatestJob({
        id: res.data.job_id,
        project_id: id,
        status: res.data.status as JobResponse['status'],
        progress: null,
        error_message: null,
        created_at: new Date().toISOString(),
        started_at: null,
        completed_at: null,
      });
    } catch (err: unknown) {
      const response = (err as { response?: { data?: { detail?: string } } })?.response;
      setAnalyzeError(response?.data?.detail || 'Failed to start analysis');
    } finally {
      setAnalyzing(false);
    }
  }

  if (loading) return <p className="text-gray-500">Loading...</p>;
  if (error || !project) {
    return (
      <div>
        <Link to="/" className="text-sm text-blue-600 hover:underline">&larr; Back to projects</Link>
        <p className="mt-4 text-red-600">{error || 'Project not found'}</p>
      </div>
    );
  }

  const jobIsActive = latestJob?.status === 'pending' || latestJob?.status === 'running';

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

      {/* Analysis section */}
      <div className="mb-6 rounded-lg border border-gray-200 bg-white p-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">QA Analysis</h2>
            {latestJob && (
              <JobStatusBadge job={latestJob} />
            )}
            {!latestJob && (
              <p className="text-sm text-gray-500 mt-1">No analysis has been run yet</p>
            )}
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleAnalyze}
              disabled={analyzing || jobIsActive || chapters.length === 0}
              className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-500 disabled:opacity-50"
            >
              {jobIsActive ? 'Analyzing...' : 'Run Analysis'}
            </button>
            {latestJob?.status === 'completed' && (
              <Link
                to={`/projects/${id}/report`}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
              >
                View Report
              </Link>
            )}
          </div>
        </div>
        {analyzeError && (
          <p className="mt-3 text-sm text-red-600">{analyzeError}</p>
        )}
      </div>

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Chapters</h2>
        <Link
          to={`/projects/${id}/upload`}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
        >
          Upload Chapter
        </Link>
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

function JobStatusBadge({ job }: { job: JobResponse }) {
  const styles: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  };

  const labels: Record<string, string> = {
    pending: 'Queued...',
    running: 'Analyzing...',
    completed: 'Analysis complete',
    failed: 'Analysis failed',
  };

  return (
    <div className="mt-1">
      <div className="flex items-center gap-2">
        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[job.status]}`}>
          {job.status === 'running' && (
            <svg className="mr-1 h-3 w-3 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          )}
          {labels[job.status]}
        </span>
        {job.status === 'failed' && job.error_message && (
          <span className="text-xs text-red-600">{job.error_message}</span>
        )}
      </div>
      {job.progress && (job.status === 'running' || job.status === 'pending') && (
        <p className="mt-1 text-xs text-blue-600">{job.progress}</p>
      )}
    </div>
  );
}
