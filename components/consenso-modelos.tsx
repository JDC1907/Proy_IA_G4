"use client"

import { Users, Check } from "lucide-react"
import type { Resultado } from "@/lib/clasificador"
import { MODELOS } from "@/lib/clasificador"
import { pct } from "@/lib/formato"
import { ModelIcon } from "./model-icon"

export function ConsensoModelos({ r }: { r: Resultado }) {
  const iconoDe = (clave: string) => MODELOS.find((m) => m.clave === clave)?.icono ?? "logistic"

  return (
    <section className="rounded-xl border border-border bg-card p-5">
      <h2 className="mb-4 flex items-center gap-2 font-semibold text-foreground">
        <Users className="h-4.5 w-4.5 text-primary" strokeWidth={1.8} aria-hidden />
        Consenso de modelos <span className="text-muted-foreground">({r.totalModelos})</span>
      </h2>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {r.modelos.map((m) => {
          const ok = m.clasifica === "AUTÉNTICA"
          const color = ok ? "var(--authentic)" : "var(--fake)"
          return (
            <div key={m.clave} className="rounded-lg border border-border p-3">
              <div className="flex items-center gap-2 text-muted-foreground">
                <ModelIcon icono={iconoDe(m.clave)} className="h-4.5 w-4.5" />
                <span className="text-xs font-medium leading-tight text-foreground">{m.nombre}</span>
              </div>
              <div className="num mt-2 text-lg font-bold text-foreground">{pct(m.probabilidad)}</div>
              <div className="mt-1 flex items-center gap-1 text-[11px] font-semibold" style={{ color }}>
                <Check className="h-3 w-3" strokeWidth={3} aria-hidden />
                {m.clasifica}
              </div>
            </div>
          )
        })}
      </div>

      <p className="mt-4 text-center text-sm text-muted-foreground">
        {r.consenso === r.totalModelos
          ? `Todos los modelos clasifican esta cuenta como ${r.veredicto.toLowerCase()}. `
          : `${r.consenso} de ${r.totalModelos} modelos clasifican esta cuenta como ${r.veredicto.toLowerCase()}. `}
        <span className="font-semibold text-foreground">
          Consenso: {r.consenso} de {r.totalModelos} modelos.
        </span>
      </p>
    </section>
  )
}
