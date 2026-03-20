export interface Project {
  id: string;
  title: string;
  description: string | null;
  source_language: string;
  target_language: string;
  created_at: string;
  updated_at: string;
}

export interface Chapter {
  id: string;
  project_id: string;
  chapter_number: number;
  title: string | null;
  created_at: string;
}

export interface ChapterDetail extends Chapter {
  dialogue_line_count: number;
}

export interface PanelInput {
  panel_id: number;
  speaker: string | null;
  text: string;
  type: 'dialogue' | 'sfx' | 'narration' | 'sign';
}

export interface PageInput {
  page_number: number;
  panels: PanelInput[];
}

export interface ChapterUpload {
  chapter_number: number;
  title: string | null;
  pages: PageInput[];
}

export type CheckerType = 'untranslated' | 'consistency' | 'voice' | 'tone';
export type Severity = 'critical' | 'warning' | 'info';
export type JobStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface JobResponse {
  id: string;
  project_id: string;
  status: JobStatus;
  progress: string | null;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface DialogueLineContext {
  page_number: number;
  panel_id: number;
  speaker: string | null;
  text: string;
  line_type: string;
}

export interface QAResult {
  id: string;
  checker_type: CheckerType;
  severity: Severity;
  title: string;
  description: string;
  suggestion: string | null;
  context: Record<string, unknown> | null;
  dialogue_line: DialogueLineContext | null;
}

export interface ReportSummary {
  total_issues: number;
  by_severity: Record<string, number>;
  by_checker: Record<string, number>;
}

export interface ReportResponse {
  project_id: string;
  job_id: string;
  job_completed_at: string | null;
  summary: ReportSummary;
  issues: QAResult[];
}
