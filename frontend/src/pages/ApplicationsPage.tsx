import { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { ApplicationForm } from "@/components/applications/ApplicationForm"
import { ApplicationTable } from "@/components/applications/ApplicationTable"
import { api } from "@/lib/api"
import type { Application } from "@/types/application"

export default function ApplicationsPage() {
  const [items, setItems] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [editingItem, setEditingItem] = useState<Application | null>(null)

  async function loadApplications() {
    setLoading(true)
    try {
      const res = await api.get<Application[]>("/applications")
      setItems(res.data)
    } catch (error) {
      console.error("Failed to load applications:", error)
      setItems([])
    } finally {
      setLoading(false)
    }
  }

  function handleSaved() {
    setEditingItem(null)
    loadApplications()
  }

  function handleCancelEdit() {
    setEditingItem(null)
  }

  useEffect(() => {
    loadApplications()
  }, [])

  return (
    <AppShell title="ApplyFlow">
      <div className="grid gap-6">
        <ApplicationForm
          editingItem={editingItem}
          onSaved={handleSaved}
          onCancelEdit={handleCancelEdit}
        />

        {loading ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading...</div>
        ) : (
          <ApplicationTable
            items={items}
            onEdit={setEditingItem}
            onDeleted={loadApplications}
          />
        )}
      </div>
    </AppShell>
  )
}