"use client"

import { Table2, Eye, Download } from "lucide-react"
import { pct } from "@/lib/formato"

export interface ResumenArchivo {
  nombre: string
  total: number
  autenticas: number
  falsas: number
}

export function ResumenArchivoCard({
  resumen,
  onVer,
  onDescargar,
}: {
  resumen: ResumenArchivo | null
  onVer: () => void
  onDescargar: () => void
}) {
  return (
    <section className="rounded-xl border border-border bg-card p-5">
      <h2 className="mb-4 flex items-center gap-2 font-semibold text-foreground">
        <Table2 className="h-4.5 w-4.5 text-primary" strokeWidth={1.8} aria-hidden />
        Análisis de archivos <span className="text-muted-foreground">(resumen)</span>
      </h2>

      {resumen ? (
        <>
          <dl className="flex flex-col divide-y divide-border">
            <Fila etiqueta="Último análisis">
              <span className="num truncate text-sm font-medium text-foreground">{resumen.nombre}</span>
            </Fila>
            <Fila etiqueta="Cuentas analizadas">
              <span className="num text-sm font-bold text-foreground">{resumen.total}</span>
            </Fila>
            <Fila etiqueta="Auténticas">
              <span className="num text-sm font-bold text-authentic">
                {resumen.autenticas} ({pct(resumen.autenticas / resumen.total)})
              </span>
            </Fila>
            <Fila etiqueta="Falsas">
              <span className="num text-sm font-bold text-fake">
                {resumen.falsas} ({pct(resumen.falsas / resumen.total)})
              </span>
            </Fila>
          </dl>

          <button
            onClick={onVer}
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg border border-border bg-card px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-muted/60"
          >
            <Eye className="h-4 w-4" strokeWidth={1.8} aria-hidden />
            Ver resultados completos
          </button>
          <button
            onClick={onDescargar}
            className="mt-2 flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-primary transition-colors hover:bg-primary-soft/60"
          >
            <Download className="h-4 w-4" strokeWidth={1.8} aria-hidden />
            Descargar resultados (CSV)
          </button>
        </>
      ) : (
        <p className="text-sm text-muted-foreground">
          Aún no has analizado ningún archivo. Ve a la pestaña{" "}
          <span className="font-medium text-foreground">Analizar un archivo</span> para procesar un CSV con varias
          cuentas.
        </p>
      )}
    </section>
  )
}

function Fila({ etiqueta, children }: { etiqueta: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3 py-2.5">
      <dt className="text-sm text-muted-foreground">{etiqueta}</dt>
      <dd className="min-w-0">{children}</dd>
    </div>
  )
}
