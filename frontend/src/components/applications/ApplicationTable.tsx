import { useState } from "react"
import { api } from "@/lib/api"
import type { Application, ApplicationStatus } from "@/types/application"

type Props = {
  items: Application[]
  onEdit: (item: Application) => void
  onDeleted: () => void
}

const statusOptions: ApplicationStatus[] = [
  "draft",
  "sent",
  "in_review",
  "interview",
  "rejected",
  "accepted",
]

function statusClass(status: string) {
  switch (status) {
    case "sent":
      return "bg-blue-100 text-blue-700"
    case "in_review":
      return "bg-yellow-100 text-yellow-800"
    case "interview":
      return "bg-purple-100 text-purple-700"
    case "rejected":
      return "bg-red-100 text-red-700"
    case "accepted":
      return "bg-green-100 text-green-700"
    default:
      return "bg-slate-100 text-slate-700"
  }
}

function formatDate(dateString: string | null) {
  if (!dateString) return "—"
  return new Date(dateString).toLocaleDateString("de-DE")
}

export function ApplicationTable({ items, onEdit, onDeleted }: Props) {
  const [editingStatusId, setEditingStatusId] = useState<number | null>(null)

  async function handleDelete(id: number) {
    if (!window.confirm("Delete this application?")) return
    await api.delete(`/applications/${id}`)
    onDeleted()
  }

  async function updateStatus(item: Application, newStatus: ApplicationStatus) {
    try {
      await api.patch(`/applications/${item.id}`, {
        status: newStatus,
      })
      setEditingStatusId(null)
      onDeleted()
    } catch (e) {
      console.error("Failed to update status", e)
    }
  }

  return (
    <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-2.5">Company</th>
            <th className="px-4 py-2.5">Position</th>
            <th className="px-4 py-2.5">Location</th>
            <th className="px-4 py-2.5">Status</th>
            <th className="px-4 py-2.5 min-w-[110px]">Applied</th>
            <th className="px-4 py-2.5">Job</th>
            <th className="px-4 py-2.5">Actions</th>
          </tr>
        </thead>

        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-t hover:bg-slate-50">
              <td className="px-4 py-2.5 font-medium">{item.company}</td>
              <td className="px-4 py-2.5">{item.position}</td>
              <td className="px-4 py-2.5">{item.location ?? "—"}</td>

              <td className="px-4 py-2.5">
                {editingStatusId === item.id ? (
                  <select
                    className="rounded-lg border px-2 py-1 text-xs"
                    value={item.status}
                    onChange={(e) =>
                      updateStatus(item, e.target.value as ApplicationStatus)
                    }
                    onBlur={() => setEditingStatusId(null)}
                    autoFocus
                  >
                    {statusOptions.map((status) => (
                      <option key={status} value={status}>
                        {status}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span
                    onClick={() => setEditingStatusId(item.id)}
                    className={`cursor-pointer rounded-full px-2.5 py-1 text-xs font-medium ${statusClass(item.status)}`}
                  >
                    {item.status}
                  </span>
                )}
              </td>

              <td className="px-4 py-2.5 whitespace-nowrap">
                {formatDate(item.applied_date)}
              </td>

              <td className="px-4 py-2.5">
                {item.job_url ? (
                  <a
                    href={item.job_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    Open
                  </a>
                ) : (
                  "—"
                )}
              </td>

              <td className="px-4 py-2.5">
                <div className="flex gap-2">
                  <button
                    onClick={() => onEdit(item)}
                    className="rounded-lg border px-2.5 py-1 text-xs"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="rounded-lg border border-red-200 px-2.5 py-1 text-xs text-red-600"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}