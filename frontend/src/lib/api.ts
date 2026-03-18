import axios from "axios"


export const api = axios.create({
  baseURL: "http://localhost:8000",
})

import type { ApplicationEvent } from "@/types/applicationEvent";

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

