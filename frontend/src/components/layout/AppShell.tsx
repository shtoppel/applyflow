import { ReactNode } from "react"

type Props = {
  title: string
  children: ReactNode
}

export function AppShell({ title, children }: Props) {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-6xl px-6 py-4">
          <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
    </div>
  )
}