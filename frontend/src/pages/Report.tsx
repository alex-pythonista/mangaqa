import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import apiClient from '../api/client';
import type { CheckerType, QAResult, ReportResponse, Severity } from '../types';

export default function Report() {
  const { id } = useParams<{ id: string }>();

  const [report, setReport] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [checkerFilter, setCheckerFilter] = useState<CheckerType | ''>('');
  const [severityFilter, setSeverityFilter] = useState<Severity | ''>('');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    async function fetchReport() {
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.get<ReportResponse>(`/api/projects/${id}/report`);
        setReport(res.data);
      } catch (err: unknown) {
        const status = (err as { response?: { status?: number } })?.response?.status;
        if (status === 404) {
          setError('No analysis has been run yet. Go back and run analysis first.');
        } else {
          setError('Failed to load report');
        }
      } finally {
        setLoading(false);
      }
    }
    fetchReport();
  }, [id]);

  if (loading) return <p className="text-gray-500">Loading report...</p>;

  if (error || !report) {
    return (
      <div>
        <Link to={`/projects/${id}`} className="text-sm text-blue-600 hover:underline">&larr; Back to project</Link>
        <p className="mt-4 text-gray-600">{error || 'No report available'}</p>
      </div>
    );
  }

  const filtered = report.issues.filter((issue) => {
    if (checkerFilter && issue.checker_type !== checkerFilter) return false;
    if (severityFilter && issue.severity !== severityFilter) return false;
    return true;
  });

  return (
    <div>
      <Link to={`/projects/${id}`} className="text-sm text-blue-600 hover:underline">&larr; Back to project</Link>
      <h1 className="mt-4 text-3xl font-bold text-gray-900 mb-6">QA Report</h1>

      {/* Summary cards */}
      <div className="grid grid-cols-2 gap-4 mb-6 sm:grid-cols-4">
        <SummaryCard label="Total Issues" value={report.summary.total_issues} color="gray" />
        <SummaryCard label="Critical" value={report.summary.by_severity.critical || 0} color="red" />
        <SummaryCard label="Warnings" value={report.summary.by_severity.warning || 0} color="amber" />
        <SummaryCard label="Info" value={report.summary.by_severity.info || 0} color="blue" />
      </div>

      {/* Checker breakdown */}
      <div className="grid grid-cols-2 gap-4 mb-6 sm:grid-cols-4">
        {(['untranslated', 'consistency', 'voice', 'tone'] as CheckerType[]).map((type) => (
          <div key={type} className="rounded-lg border border-gray-200 bg-white px-4 py-3">
            <p className="text-xs text-gray-500 capitalize">{type}</p>
            <p className="text-lg font-semibold text-gray-900">{report.summary.by_checker[type] || 0}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <select
          value={checkerFilter}
          onChange={(e) => setCheckerFilter(e.target.value as CheckerType | '')}
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="">All Checkers</option>
          <option value="untranslated">Untranslated</option>
          <option value="consistency">Consistency</option>
          <option value="voice">Voice</option>
          <option value="tone">Tone</option>
        </select>
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value as Severity | '')}
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
        </select>
        <span className="self-center text-sm text-gray-500">
          {filtered.length} issue{filtered.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Issue list */}
      {filtered.length === 0 ? (
        <p className="text-gray-500">
          {report.summary.total_issues === 0 ? 'No issues found — great job!' : 'No issues match the current filters.'}
        </p>
      ) : (
        <div className="grid gap-3">
          {filtered.map((issue) => (
            <IssueCard
              key={issue.id}
              issue={issue}
              expanded={expandedId === issue.id}
              onToggle={() => setExpandedId(expandedId === issue.id ? null : issue.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function SummaryCard({ label, value, color }: { label: string; value: number; color: string }) {
  const bg: Record<string, string> = {
    gray: 'bg-gray-50 border-gray-200',
    red: 'bg-red-50 border-red-200',
    amber: 'bg-amber-50 border-amber-200',
    blue: 'bg-blue-50 border-blue-200',
  };
  const text: Record<string, string> = {
    gray: 'text-gray-900',
    red: 'text-red-700',
    amber: 'text-amber-700',
    blue: 'text-blue-700',
  };

  return (
    <div className={`rounded-lg border px-4 py-3 ${bg[color]}`}>
      <p className="text-xs text-gray-500">{label}</p>
      <p className={`text-2xl font-bold ${text[color]}`}>{value}</p>
    </div>
  );
}

function IssueCard({ issue, expanded, onToggle }: { issue: QAResult; expanded: boolean; onToggle: () => void }) {
  const severityStyles: Record<string, string> = {
    critical: 'bg-red-100 text-red-800',
    warning: 'bg-amber-100 text-amber-800',
    info: 'bg-blue-100 text-blue-800',
  };

  const checkerStyles: Record<string, string> = {
    untranslated: 'bg-purple-100 text-purple-800',
    consistency: 'bg-teal-100 text-teal-800',
    voice: 'bg-indigo-100 text-indigo-800',
    tone: 'bg-orange-100 text-orange-800',
  };

  return (
    <div
      className="rounded-lg border border-gray-200 bg-white overflow-hidden cursor-pointer"
      onClick={onToggle}
    >
      <div className="px-5 py-4">
        <div className="flex items-start gap-3">
          <div className="flex gap-2 shrink-0">
            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${severityStyles[issue.severity]}`}>
              {issue.severity}
            </span>
            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${checkerStyles[issue.checker_type]}`}>
              {issue.checker_type}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium text-gray-900">{issue.title}</p>
            {issue.dialogue_line && (
              <p className="mt-0.5 text-xs text-gray-400">
                Page {issue.dialogue_line.page_number}, Panel {issue.dialogue_line.panel_id}
                {issue.dialogue_line.speaker && ` — ${issue.dialogue_line.speaker}`}
              </p>
            )}
          </div>
          <svg
            className={`h-5 w-5 text-gray-400 transition-transform ${expanded ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {expanded && (
        <div className="border-t border-gray-100 px-5 py-4 bg-gray-50">
          <p className="text-sm text-gray-700">{issue.description}</p>

          {issue.dialogue_line && (
            <div className="mt-3 rounded-md bg-white border border-gray-200 px-4 py-3">
              <p className="text-xs text-gray-500 mb-1">Dialogue Line</p>
              <p className="text-sm text-gray-900">
                {issue.dialogue_line.speaker && (
                  <span className="font-medium">{issue.dialogue_line.speaker}: </span>
                )}
                &ldquo;{issue.dialogue_line.text}&rdquo;
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Type: {issue.dialogue_line.line_type}
              </p>
            </div>
          )}

          {issue.suggestion && (
            <div className="mt-3">
              <p className="text-xs text-gray-500 mb-1">Suggestion</p>
              <p className="text-sm text-green-700">{issue.suggestion}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
