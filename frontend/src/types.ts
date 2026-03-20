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
