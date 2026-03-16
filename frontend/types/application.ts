export type ApplicationStatus =
  | "draft"
  | "sent"
  | "in_review"
  | "interview"
  | "rejected"
  | "accepted"

export interface Application {
  id: number
  company: string
  position: string
  location: string | null
  status: ApplicationStatus
  applied_date: string | null
  job_url: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface CreateApplicationPayload {
  company: string
  position: string
  location?: string | null
  status?: ApplicationStatus
  applied_date?: string | null
  job_url?: string | null
  notes?: string | null
}

export interface UpdateApplicationPayload {
  company?: string
  position?: string
  location?: string | null
  status?: ApplicationStatus
  applied_date?: string | null
  job_url?: string | null
  notes?: string | null
}