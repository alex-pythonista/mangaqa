import { useState } from 'react';
import apiClient from '../api/client';

interface HealthStatus {
  backend: string;
  database: string;
  database_error: string | null;
}

export default function Dashboard() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function checkHealth() {
    setLoading(true);
    setError(null);
    setHealth(null);

    try {
      const res = await apiClient.get<HealthStatus>('/health');
      setHealth(res.data);
    } catch {
      setError('Cannot reach backend');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="mb-8 rounded-lg border border-gray-200 bg-white p-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">System Status</h2>
            <p className="text-sm text-gray-500">Check if backend and database are connected</p>
          </div>
          <button
            onClick={checkHealth}
            disabled={loading}
            className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50"
          >
            {loading ? 'Checking...' : 'Check Backend'}
          </button>
        </div>

        {error && (
          <div className="mt-4 flex items-center gap-3 rounded-md bg-red-50 px-4 py-3">
            <span className="text-red-600 text-lg">&#x2717;</span>
            <div>
              <p className="text-sm font-medium text-red-800">Backend unreachable</p>
              <p className="text-sm text-red-600">{error}</p>
            </div>
          </div>
        )}

        {health && (
          <div className="mt-4 flex flex-col gap-3">
            <StatusRow
              label="Backend"
              status={health.backend}
              error={null}
            />
            <StatusRow
              label="Database"
              status={health.database}
              error={health.database_error}
            />
          </div>
        )}
      </div>

      <h1 className="text-3xl font-bold text-gray-900 mb-4">Projects</h1>
      <p className="text-gray-600">Your manga translation QA projects will appear here.</p>
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
