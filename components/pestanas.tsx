"use client"

import { Search, FileText, Info } from "lucide-react"

export type Pestana = "cuenta" | "archivo" | "acerca"

const TABS: { id: Pestana; label: string; Icon: typeof Search }[] = [
  { id: "cuenta", label: "Analizar una cuenta", Icon: Search },
  { id: "archivo", label: "Analizar un archivo", Icon: FileText },
  { id: "acerca", label: "Acerca del sistema", Icon: Info },
]

export function Pestanas({
  activa,
  onCambiar,
}: {
  activa: Pestana
  onCambiar: (p: Pestana) => void
}) {
  return (
    <div className="grid grid-cols-1 gap-1 rounded-xl border border-border bg-card p-1 sm:grid-cols-3" role="tablist">
      {TABS.map(({ id, label, Icon }) => {
        const sel = activa === id
        return (
          <button
            key={id}
            role="tab"
            aria-selected={sel}
            onClick={() => onCambiar(id)}
            className={`flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors ${
              sel
                ? "bg-primary-soft text-primary"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            }`}
          >
            <Icon className="h-4 w-4" strokeWidth={1.8} aria-hidden />
            {label}
          </button>
        )
      })}
    </div>
  )
}
