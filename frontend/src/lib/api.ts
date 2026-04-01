import axios from "axios";
import type { ApplicationEvent } from "@/types/applicationEvent";

export const api = axios.create({
  baseURL: "http://localhost:8000",
});

function formatTimestampForFilename(date: Date): string {
  const pad = (value: number) => String(value).padStart(2, "0");

  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  const seconds = pad(date.getSeconds());

  return `${year}-${month}-${day}_${hours}-${minutes}-${seconds}`;
}

export async function getRecentEvents(): Promise<ApplicationEvent[]> {
  const response = await fetch("http://localhost:8000/events/recent");

  if (!response.ok) {
    throw new Error("Failed to fetch recent events");
  }

  return response.json();
}

export async function syncGmailAndUpdate() {
  const response = await fetch("http://localhost:8000/gmail/sync-and-update", {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Failed to sync Gmail");
  }

  return response.json();
}

export async function downloadApplicationsExport(
  format: "csv" | "json" | "backup",
  statusFilter?: string
) {
  const params = new URLSearchParams();

  if (statusFilter && statusFilter !== "all" && format !== "backup") {
    params.set("status_filter", statusFilter);
  }

  const endpoint =
    format === "backup"
      ? "/applications/export/backup"
      : `/applications/export/${format}`;

  const query = params.toString();
  const baseUrl = api.defaults.baseURL ?? "http://localhost:8000";
  const url = `${baseUrl}${endpoint}${query ? `?${query}` : ""}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Export failed with status ${response.status}`);
  }

  const blob = await response.blob();
  const objectUrl = window.URL.createObjectURL(blob);

  const timestamp = formatTimestampForFilename(new Date());

  const a = document.createElement("a");
  a.href = objectUrl;

  if (format === "csv") {
    a.download = `applyflow_export_${timestamp}.csv`;
  } else if (format === "json") {
    a.download = `applyflow_export_${timestamp}.json`;
  } else {
    a.download = `applyflow_backup_${timestamp}.json`;
  }

  document.body.appendChild(a);
  a.click();
  a.remove();

  window.URL.revokeObjectURL(objectUrl);
}