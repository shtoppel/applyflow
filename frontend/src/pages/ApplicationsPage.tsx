import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ApplicationForm } from "@/components/applications/ApplicationForm";
import { ApplicationTable } from "@/components/applications/ApplicationTable";
import { api, downloadApplicationsExport } from "@/lib/api";
import type { Application, ApplicationStatus } from "@/types/application";

const statusOptions: { label: string; value: "all" | ApplicationStatus }[] = [
  { label: "All", value: "all" },
  { label: "Draft", value: "draft" },
  { label: "Sent", value: "sent" },
  { label: "In Review", value: "in_review" },
  { label: "Interview", value: "interview" },
  { label: "Rejected", value: "rejected" },
  { label: "Accepted", value: "accepted" },
];

type ApplicationsPageProps = {
  refreshToken: number;
};

export default function ApplicationsPage({
  refreshToken,
}: ApplicationsPageProps) {
  const [items, setItems] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingItem, setEditingItem] = useState<Application | null>(null);
  const [statusFilter, setStatusFilter] = useState<"all" | ApplicationStatus>(
    "all"
  );

  async function loadApplications() {
    setLoading(true);
    try {
      const res = await api.get<Application[]>("/applications");
      setItems(res.data);
    } catch (error) {
      console.error("Failed to load applications:", error);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  function handleSaved() {
    setEditingItem(null);
    loadApplications();
  }

  function handleCancelEdit() {
    setEditingItem(null);
  }

  useEffect(() => {
    loadApplications();
  }, [refreshToken]);

  const filteredItems = useMemo(() => {
    const sorted = [...items].sort((a, b) => {
      const dateA = a.applied_date ?? a.created_at;
      const dateB = b.applied_date ?? b.created_at;
      return new Date(dateB).getTime() - new Date(dateA).getTime();
    });

    if (statusFilter === "all") return sorted;
    return sorted.filter((item) => item.status === statusFilter);
  }, [items, statusFilter]);

  const stats = useMemo(() => {
    const total = items.length;
    const active = items.filter(
      (item) => item.status === "sent" || item.status === "in_review"
    ).length;
    const rejected = items.filter((item) => item.status === "rejected").length;
    const rejectionRate = total > 0 ? Math.round((rejected / total) * 100) : 0;

    return {
      total,
      active,
      rejected,
      rejectionRate,
    };
  }, [items]);

  return (
    <AppShell title="ApplyFlow">
      <div className="grid gap-4">
        <ApplicationForm
          editingItem={editingItem}
          onSaved={handleSaved}
          onCancelEdit={handleCancelEdit}
        />

        <div className="flex items-center justify-between rounded-2xl border bg-white p-4 shadow-sm">
          <div>
            <div className="text-sm font-medium text-slate-900">Applications</div>
            <div className="text-sm text-slate-500">
              {stats.total} total · {stats.active} active · {stats.rejected} rejected ·{" "}
              {stats.rejectionRate}% rejection rate
            </div>
          </div>

         <div className="flex items-center gap-3">
  <label className="text-sm text-slate-600" htmlFor="export-select">
    Export
  </label>
  <select
    id="export-select"
    className="rounded-xl border px-3 py-2 text-sm"
    defaultValue=""
    onChange={async (e) => {
      const value = e.target.value;
      if (!value) return;

      try {
        if (value === "csv") {
          await downloadApplicationsExport("csv", statusFilter);
        }

        if (value === "json") {
          await downloadApplicationsExport("json", statusFilter);
        }

        if (value === "backup") {
          await downloadApplicationsExport("backup");
        }
      } catch (error) {
        console.error("Export failed:", error);
        alert("Export failed");
      } finally {
        e.target.value = "";
      }
    }}
  >
    <option value="">Select</option>
    <option value="csv">CSV (current filter)</option>
    <option value="json">JSON (current filter)</option>
    <option value="backup">Full Backup</option>
  </select>

  <label className="text-sm text-slate-600" htmlFor="status-filter">
    Status
  </label>
  <select
    id="status-filter"
    className="rounded-xl border px-3 py-2 text-sm"
    value={statusFilter}
    onChange={(e) =>
      setStatusFilter(e.target.value as "all" | ApplicationStatus)
    }
  >
    {statusOptions.map((option) => (
      <option key={option.value} value={option.value}>
        {option.label}
      </option>
    ))}
  </select>

          </div>
        </div>

        {loading ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading...</div>
        ) : filteredItems.length === 0 ? (
          <div className="rounded-2xl border bg-white p-8 text-center shadow-sm">
            <div className="text-lg font-semibold text-slate-900">
              No applications found
            </div>
            <div className="mt-2 text-sm text-slate-500">
              Add your first application or change the current filter.
            </div>
          </div>
        ) : (
          <ApplicationTable
            items={filteredItems}
            onEdit={setEditingItem}
            onDeleted={loadApplications}
          />
        )}
      </div>
    </AppShell>
  );
}