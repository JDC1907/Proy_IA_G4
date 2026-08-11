import { Instagram, GraduationCap } from "lucide-react"

export function Encabezado() {
  return (
    <header className="flex items-start justify-between gap-4">
      <div className="flex items-start gap-3">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-fuchsia-500 via-rose-500 to-amber-400 text-white shadow-sm">
          <Instagram className="h-6 w-6" strokeWidth={2} aria-hidden />
        </div>
        <div>
          <h1 className="text-pretty text-2xl font-bold tracking-tight text-foreground">
            Clasificador de cuentas de Instagram
          </h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            Detecta si una cuenta es auténtica o falsa usando IA y datos públicos.
          </p>
        </div>
      </div>
      <div className="hidden shrink-0 items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 sm:flex">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary-soft text-primary">
          <GraduationCap className="h-4.5 w-4.5" strokeWidth={1.8} aria-hidden />
        </div>
        <div className="leading-tight">
          <div className="text-sm font-semibold text-foreground">Proyecto de IA</div>
          <div className="text-xs text-muted-foreground">Universidad</div>
        </div>
      </div>
    </header>
  )
}
