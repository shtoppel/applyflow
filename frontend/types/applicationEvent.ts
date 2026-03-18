export type ApplicationEvent = {
  id: number;
  application_id: number;
  event_type: string;
  source: string;
  old_status: string | null;
  new_status: string | null;
  message: string | null;
  gmail_message_id: string | null;
  created_at: string;
  company: string | null;
  position: string | null;
};