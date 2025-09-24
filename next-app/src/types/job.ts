export type JobCategory = 'cybersecurity' | 'software-engineering'

export type ExperienceLevel = 'entry' | 'mid' | 'senior' | 'lead' | 'executive'

export type JobSource = 'indeed' | 'linkedin' | 'glassdoor' | 'ziprecruiter' | 'dice' | 'wellfound' | 'google-dorks'

export type TimeFilter = '12h' | '24h' | '3d' | '7d' | '14d' | '30d'

export interface Job {
  id: string
  title: string
  company: string
  location: string
  description: string
  url: string
  source: JobSource
  posted_date: string
  experience_level?: ExperienceLevel
  salary_range?: string
  classification_tags: string[]
  sponsored: boolean
  remote_friendly: boolean
  visa_sponsorship: boolean
  security_clearance_required: boolean
  created_at: string
  updated_at: string
}

export interface JobSearchFilters {
  category: JobCategory
  keywords?: string
  location: string
  sources: JobSource[]
  experience_level: ExperienceLevel | 'all'
  time_filter: TimeFilter
  max_pages: number
  exclude_citizenship_required: boolean
  f1_student_friendly: boolean
  remote_only: boolean
  exclude_easy_apply: boolean
  use_google_dorks: boolean
  serp_api_key?: string
}

export interface JobSearchResult {
  jobs: Job[]
  total_count: number
  filters_applied: JobSearchFilters
  search_id: string
  created_at: string
  sources_scraped: JobSource[]
  scraping_duration: number
}

export interface JobStats {
  total_jobs: number
  by_source: Record<JobSource, number>
  by_experience_level: Record<ExperienceLevel, number>
  by_location: Record<string, number>
  by_company: Record<string, number>
  remote_jobs: number
  visa_sponsorship_jobs: number
  security_clearance_jobs: number
  average_posting_age: number
}

export interface ScrapingProgress {
  id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  current_source?: JobSource
  message: string
  jobs_found: number
  sources_completed: JobSource[]
  started_at: string
  completed_at?: string
  error?: string
}
