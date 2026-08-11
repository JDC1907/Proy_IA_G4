"use client"

import { Scale, BarChart3, ArrowUp, ArrowDown, Check, X, Minus } from "lucide-react"
import type { Resultado } from "@/lib/clasificador"
import { describirAporte } from "@/lib/clasificador"
import { ATRIBUTOS } from "@/lib/atributos"
import { num, ordinal } from "@/lib/formato"

const DIR = {
  autentica: { color: "var(--authentic)", Icon: Check, label: "Aporta a AUTÉNTICA" },
  falsa: { color: "var(--fake)", Icon: X, label: "Aporta a FALSA" },
  bajo: { color: "var(--ambiguous)", Icon: Minus, label: "Impacto bajo" },
}

export function SenalesComparacion({ r }: { r: Resultado }) {
  const top = r.aportes.slice(0, 5)

  return (
    <section className="grid gap-4 lg:grid-cols-5">
      {/* Señales */}
      <div className="rounded-xl border border-border bg-card p-5 lg:col-span-3">
        <div className="mb-1 flex items-center gap-2">
          <Scale className="h-4.5 w-4.5 text-primary" strokeWidth={1.8} aria-hidden />
          <h2 className="font-semibold text-foreground">Qué señales influyeron en la decisión</h2>
        </div>
        <p className="mb-4 text-sm text-muted-foreground">Las variables con mayor impacto en el resultado</p>

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {top.map((a) => {
            const d = DIR[a.direccion]
            const at = ATRIBUTOS[a.clave]
            const valorMostrado =
              at.unidad === "%" ? `${num(a.valor)}%` : at.tipo === "binario" ? (a.valor >= 0.5 ? "Sí" : "No") : num(a.valor)
            return (
              <div key={a.clave} className="flex flex-col rounded-lg border border-border p-3">
                <div className="flex items-center gap-1.5">
                  <d.Icon className="h-4 w-4" style={{ color: d.color }} strokeWidth={2.5} aria-hidden />
                  <span className="num font-semibold text-foreground">{a.clave}</span>
                </div>
                <div className="mt-1 flex items-baseline gap-1">
                  <span className="num text-lg font-bold text-foreground">{valorMostrado}</span>
                  {a.direccion !== "bajo" &&
                    (a.direccion === "autentica" ? (
                      <ArrowUp className="h-3.5 w-3.5" style={{ color: d.color }} strokeWidth={2.5} aria-hidden />
                    ) : (
                      <ArrowDown className="h-3.5 w-3.5" style={{ color: d.color }} strokeWidth={2.5} aria-hidden />
                    ))}
                </div>
                <p className="mt-1 flex-1 text-xs leading-snug text-muted-foreground">{describirAporte(a)}</p>
                <span
                  className="mt-2 inline-flex w-fit items-center rounded-md px-2 py-0.5 text-[11px] font-semibold"
                  style={{ color: d.color, backgroundColor: `color-mix(in srgb, ${d.color} 12%, transparent)` }}
                >
                  {d.label}
                </span>
              </div>
            )
          })}
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-1 border-t border-border pt-3 text-xs text-muted-foreground">
          <Leyenda color="var(--authentic)" texto="Aporta a auténtica" />
          <Leyenda color="var(--fake)" texto="Aporta a falsa" />
          <Leyenda color="var(--ambiguous)" texto="Impacto bajo" />
        </div>
      </div>

      {/* Comparación percentiles */}
      <div className="rounded-xl border border-border bg-card p-5 lg:col-span-2">
        <div className="mb-1 flex items-center gap-2">
          <BarChart3 className="h-4.5 w-4.5 text-primary" strokeWidth={1.8} aria-hidden />
          <h2 className="font-semibold text-foreground">Comparación con cuentas típicas</h2>
        </div>
        <p className="mb-4 text-sm text-muted-foreground">(percentiles)</p>

        <div className="flex flex-col gap-3.5">
          {r.percentiles.map((p) => (
            <div key={p.clave}>
              <div className="mb-1 flex items-center justify-between gap-2">
                <span className="truncate text-xs text-foreground">{p.etiqueta}</span>
                <span className="num shrink-0 text-xs font-semibold text-foreground">{ordinal(p.percentil)}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-primary"
                    style={{ width: `${Math.max(3, p.percentil)}%` }}
                  />
                </div>
              </div>
              <div className="mt-0.5 text-[11px] text-muted-foreground">{p.descripcion}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function Leyenda({ color, texto }: { color: string; texto: string }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
      {texto}
    </span>
  )
}
