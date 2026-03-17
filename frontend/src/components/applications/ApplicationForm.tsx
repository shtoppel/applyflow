import { useEffect, useState } from "react"
import { api } from "@/lib/api"
import type { Application, CreateApplicationPayload } from "@/types/application"

type Props = {
  editingItem: Application | null
  onSaved: () => void
  onCancelEdit: () => void
}

const initialState: CreateApplicationPayload = {
  company: "",
  position: "",
  location: "",
  status: "draft",
  applied_date: "",
  job_url: "",
  notes: "",
}

export function ApplicationForm({ editingItem, onSaved, onCancelEdit }: Props) {
  const [form, setForm] = useState<CreateApplicationPayload>(initialState)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (editingItem) {
      setForm({
        company: editingItem.company,
        position: editingItem.position,
        location: editingItem.location ?? "",
        status: editingItem.status,
        applied_date: editingItem.applied_date ?? "",
        job_url: editingItem.job_url ?? "",
        notes: editingItem.notes ?? "",
      })
    } else {
      setForm(initialState)
    }
  }, [editingItem])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)

    const payload = {
      ...form,
      applied_date: form.applied_date || null,
      job_url: form.job_url || null,
      location: form.location || null,
      notes: form.notes || null,
    }

    try {
      if (editingItem) {
        await api.patch(`/applications/${editingItem.id}`, payload)
      } else {
        await api.post("/applications", payload)
      }

      setForm(initialState)
      onSaved()
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl border bg-white p-6 shadow-sm">
      <div className="grid gap-4 md:grid-cols-2">
        <input
          className="rounded-lg border px-3 py-2 text-sm"
          placeholder="Company"
          value={form.company ?? ""}
          onChange={(e) => setForm({ ...form, company: e.target.value })}
          required
        />
        <input
          className="rounded-lg border px-3 py-2 text-sm"
          placeholder="Position"
          value={form.position ?? ""}
          onChange={(e) => setForm({ ...form, position: e.target.value })}
          required
        />
        <input
          className="rounded-lg border px-3 py-2 text-sm"
          placeholder="Location"
          value={form.location ?? ""}
          onChange={(e) => setForm({ ...form, location: e.target.value })}
        />
        <select
          className="rounded-lg border px-3 py-2 text-sm"
          value={form.status ?? "draft"}
          onChange={(e) => setForm({ ...form, status: e.target.value as CreateApplicationPayload["status"] })}
        >
          <option value="draft">Draft</option>
          <option value="sent">Sent</option>
          <option value="in_review">In Review</option>
          <option value="interview">Interview</option>
          <option value="rejected">Rejected</option>
          <option value="accepted">Accepted</option>
        </select>
        <input
          className="rounded-lg border px-3 py-2 text-sm"
          type="date"
          value={form.applied_date ?? ""}
          onChange={(e) => setForm({ ...form, applied_date: e.target.value })}
        />
        <input
          className="rounded-lg border px-3 py-2 text-sm"
          placeholder="Job URL"
          value={form.job_url ?? ""}
          onChange={(e) => setForm({ ...form, job_url: e.target.value })}
        />
      </div>

      <textarea
        className="min-h-28 w-full rounded-xl border px-3 py-2"
        placeholder="Notes"
        value={form.notes ?? ""}
        onChange={(e) => setForm({ ...form, notes: e.target.value })}
      />

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={loading}
          className="rounded-xl bg-slate-900 px-4 py-2 text-white disabled:opacity-50"
        >
          {loading ? "Saving..." : editingItem ? "Update application" : "Add application"}
        </button>

        {editingItem && (
          <button
            type="button"
            onClick={onCancelEdit}
            className="rounded-xl border px-4 py-2 text-slate-700"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}