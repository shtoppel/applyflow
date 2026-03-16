import { api } from "@/lib/api"
import type { Application } from "@/types/application"

type Props = {
  items: Application[]
  onEdit: (item: Application) => void
  onDeleted: () => void
}

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

export function ApplicationTable({ items, onEdit, onDeleted }: Props) {
  async function handleDelete(id: number) {
    const confirmed = window.confirm("Delete this application?")
    if (!confirmed) return

    await api.delete(`/applications/${id}`)
    onDeleted()
  }

  return (
    <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50 text-left text-slate-600">
          <tr>
            <th className="px-4 py-3">Company</th>
            <th className="px-4 py-3">Position</th>
            <th className="px-4 py-3">Location</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Applied</th>
            <th className="px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-t">
              <td className="px-4 py-3 font-medium">{item.company}</td>
              <td className="px-4 py-3">{item.position}</td>
              <td className="px-4 py-3">{item.location ?? "—"}</td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${statusClass(item.status)}`}>
                  {item.status}
                </span>
              </td>
              <td className="px-4 py-3">{item.applied_date ?? "—"}</td>
              <td className="px-4 py-3">
                <div className="flex gap-2">
                  <button
                    onClick={() => onEdit(item)}
                    className="rounded-lg border px-3 py-1.5 text-xs font-medium"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600"
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