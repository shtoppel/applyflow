import { useEffect, useState } from "react";
import { getRecentEvents, syncGmailAndUpdate } from "@/lib/api";
import type { ApplicationEvent } from "@/types/applicationEvent";

type RecentActivityWidgetProps = {
  onRefreshApplications: () => void;
};

function formatEventTitle(event: ApplicationEvent): string {
  if (event.event_type === "manual_status_change") {
    return "Manual status change";
  }

  if (event.event_type === "gmail_status_applied") {
    return "Auto status update";
  }

  if (event.event_type === "gmail_detected") {
    return "Email detected";
  }

  return event.event_type;
}

function formatTime(value: string): string {
  const date = new Date(value);
  return date.toLocaleString();
}

function sourceBadgeClass(source: string): string {
  if (source === "gmail") {
    return "bg-blue-100 text-blue-700 border border-blue-200";
  }

  if (source === "manual") {
    return "bg-emerald-100 text-emerald-700 border border-emerald-200";
  }

  return "bg-slate-100 text-slate-700 border border-slate-200";
}

export default function RecentActivityWidget({
  onRefreshApplications,
}: RecentActivityWidgetProps) {
  const [events, setEvents] = useState<ApplicationEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  const loadEvents = async () => {
    try {
      setError(null);
      const data = await getRecentEvents();

      const filtered = data.filter(
        (event) =>
          event.event_type === "manual_status_change" ||
          event.event_type === "gmail_status_applied"
      );

      setEvents(filtered);
    } catch (err) {
      setError("Failed to load activity");
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshClick = async () => {
    setLoading(true);
    await loadEvents();
    onRefreshApplications();
  };

  const handleSyncClick = async () => {
    try {
      setError(null);
      setSyncing(true);

      await syncGmailAndUpdate();
      await loadEvents();
      onRefreshApplications();
    } catch (err) {
      setError("Failed to sync Gmail");
    } finally {
      setSyncing(false);
    }
  };

  const handleToggle = async () => {
    const nextOpen = !isOpen;
    setIsOpen(nextOpen);

    if (nextOpen && events.length === 0 && !loading) {
      setLoading(true);
      await loadEvents();
    }
  };

  useEffect(() => {
    loadEvents();
  }, []);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const interval = setInterval(loadEvents, 15000);
    return () => clearInterval(interval);
  }, [isOpen]);

  return (
    <div
      className={`fixed bottom-4 right-4 z-50 rounded-2xl border border-slate-200 bg-white shadow-xl transition-all ${
        isOpen
          ? "w-[360px] max-w-[calc(100vw-2rem)]"
          : "w-[260px] max-w-[calc(100vw-2rem)]"
      }`}
    >
      <div className="flex items-center justify-between gap-3 px-4 py-3">
        <div className="min-w-0">
          <h3 className="truncate text-sm font-semibold text-slate-800">
            Recent activity
            {!loading && events.length > 0 ? ` (${events.length})` : ""}
          </h3>
          <p className="truncate text-xs text-slate-500">
            Manual and Gmail-driven updates
          </p>
        </div>

        <button
          onClick={handleToggle}
          className="shrink-0 rounded-lg border border-slate-200 px-2 py-1 text-xs text-slate-600 hover:bg-slate-50"
        >
          {isOpen ? "Hide" : "Show"}
        </button>
      </div>

      {isOpen && (
        <>
          <div className="flex items-center justify-between gap-2 border-t border-b border-slate-100 px-4 py-3">
            <div className="text-xs text-slate-500">
              {loading ? "Loading..." : `${events.length} item(s)`}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleRefreshClick}
                className="rounded-lg border border-slate-200 px-2 py-1 text-xs text-slate-600 hover:bg-slate-50"
              >
                Refresh
              </button>

              <button
                onClick={handleSyncClick}
                disabled={syncing}
                className="rounded-lg border border-blue-200 bg-blue-50 px-2 py-1 text-xs text-blue-700 hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {syncing ? "Syncing..." : "Sync Gmail"}
              </button>
            </div>
          </div>

          <div className="max-h-[420px] overflow-y-auto p-3">
            {loading ? (
              <div className="text-sm text-slate-500">Loading activity...</div>
            ) : error ? (
              <div className="text-sm text-red-500">{error}</div>
            ) : events.length === 0 ? (
              <div className="text-sm text-slate-500">No activity yet.</div>
            ) : (
              <div className="space-y-3">
                {events.map((event) => (
                  <div
                    key={event.id}
                    className="rounded-xl border border-slate-100 bg-slate-50 p-3"
                  >
                    <div className="mb-2 flex items-start justify-between gap-2">
                      <div>
                        <div className="text-sm font-medium text-slate-800">
                          {formatEventTitle(event)}
                        </div>

                        <div className="text-xs text-slate-500">
                          {formatTime(event.created_at)}
                        </div>
                      </div>

                      <span
                        className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${sourceBadgeClass(
                          event.source
                        )}`}
                      >
                        {event.source}
                      </span>
                    </div>

                    {(event.company || event.position) && (
                      <div className="mb-2 text-xs text-slate-600">
                        {[event.company, event.position]
                          .filter(Boolean)
                          .join(" — ")}
                      </div>
                    )}

                    {(event.old_status || event.new_status) && (
                      <div className="mb-2 text-xs text-slate-700">
                        <span className="font-medium">
                          {event.old_status ?? "—"}
                        </span>
                        <span className="mx-1">→</span>
                        <span className="font-medium">
                          {event.new_status ?? "—"}
                        </span>
                      </div>
                    )}

                    {event.message && (
                      <div className="text-xs leading-5 text-slate-600">
                        {event.message}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}