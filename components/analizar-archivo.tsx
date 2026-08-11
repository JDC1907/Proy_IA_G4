"use client"

import { useRef, useState } from "react"
import { UploadCloud, FileSpreadsheet, Download, CheckCircle2 } from "lucide-react"
import { analizarCSV, generarCSVResultados, type AnalisisArchivo } from "@/lib/csv"
import { pct, num } from "@/lib/formato"

export function AnalizarArchivo({
  analisis,
  onAnalisis,
}: {
  analisis: AnalisisArchivo | null
  onAnalisis: (a: AnalisisArchivo) => void
}) {
  const [error, setError] = useState<string | null>(null)
  const [cargando, setCargando] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  async function procesar(nombre: string, texto: string) {
    setError(null)
    const res = analizarCSV(nombre, texto)
    if ("error" in res) {
      setError(res.error)
      return
    }
    onAnalisis(res)
  }

  async function onArchivo(file: File) {
    setCargando(true)
    try {
      const texto = await file.text()
      await procesar(file.name, texto)
    } finally {
      setCargando(false)
    }
  }

  async function cargarEjemplo() {
    setCargando(true)
    try {
      const res = await fetch("/ejemplos_prueba.csv")
      const texto = await res.text()
      await procesar("ejemplos_prueba.csv", texto)
    } catch {
      setError("No se pudo cargar el archivo de ejemplo.")
    } finally {
      setCargando(false)
    }
  }

  function descargar() {
    if (!analisis) return
    const blob = new Blob([generarCSVResultados(analisis)], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `resultado_${analisis.nombre}`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex flex-col gap-4">
      <section className="rounded-xl border border-border bg-card p-6">
        <h2 className="flex items-center gap-2 font-semibold text-foreground">
          <FileSpreadsheet className="h-4.5 w-4.5 text-primary" strokeWidth={1.8} aria-hidden />
          Analizar un archivo CSV
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Sube un CSV con las 17 columnas de atributos ({" "}
          <span className="num">pos, flw, flg…</span> ). Cada fila se clasifica con los 5 modelos. Si incluye la
          columna <span className="num font-medium text-foreground">class</span>, se calcula la coincidencia con la
          etiqueta real.
        </p>

        <label
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault()
            const f = e.dataTransfer.files?.[0]
            if (f) onArchivo(f)
          }}
          className="mt-4 flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-input bg-muted/30 px-6 py-10 text-center transition-colors hover:border-ring hover:bg-primary-soft/30"
        >
          <UploadCloud className="h-8 w-8 text-primary" strokeWidth={1.6} aria-hidden />
          <span className="text-sm font-medium text-foreground">
            Arrastra un archivo CSV aquí o haz clic para seleccionarlo
          </span>
          <span className="text-xs text-muted-foreground">Se procesa localmente en tu navegador</span>
          <input
            ref={inputRef}
            type="file"
            accept=".csv,text/csv"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0]
              if (f) onArchivo(f)
            }}
          />
        </label>

        <div className="mt-3 flex flex-wrap items-center gap-3">
          <button
            onClick={cargarEjemplo}
            disabled={cargando}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition-colors hover:opacity-90 disabled:opacity-60"
          >
            Usar archivo de ejemplo
          </button>
          {cargando && <span className="text-sm text-muted-foreground">Procesando…</span>}
          {error && <span className="text-sm font-medium text-fake">{error}</span>}
        </div>
      </section>

      {analisis && (
        <section className="rounded-xl border border-border bg-card p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="flex items-center gap-2 font-semibold text-foreground">
                <CheckCircle2 className="h-4.5 w-4.5 text-authentic" strokeWidth={1.8} aria-hidden />
                Resultados de <span className="num">{analisis.nombre}</span>
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">
                {analisis.total} cuentas analizadas · {analisis.autenticas} auténticas · {analisis.falsas} falsas
                {analisis.aciertos !== undefined && (
                  <> · coincidencia con la etiqueta real: {pct(analisis.aciertos)}</>
                )}
              </p>
            </div>
            <button
              onClick={descargar}
              className="flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm font-medium text-foreground transition-colors hover:bg-muted/60"
            >
              <Download className="h-4 w-4" strokeWidth={1.8} aria-hidden />
              Descargar CSV
            </button>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted-foreground">
                  <th className="py-2 pr-3 font-medium">#</th>
                  <th className="py-2 pr-3 font-medium">Veredicto</th>
                  <th className="py-2 pr-3 font-medium">Prob. autenticidad</th>
                  <th className="py-2 pr-3 font-medium">Consenso</th>
                  <th className="py-2 pr-3 font-medium">Confianza</th>
                  <th className="py-2 pr-3 font-medium">Etiqueta real</th>
                </tr>
              </thead>
              <tbody>
                {analisis.filas.map((f) => {
                  const ok = f.resultado.veredicto === "AUTÉNTICA"
                  const acierto = f.etiquetaReal ? f.etiquetaReal === f.resultado.veredicto : undefined
                  return (
                    <tr key={f.indice} className="border-b border-border/60">
                      <td className="num py-2 pr-3 text-muted-foreground">{f.indice}</td>
                      <td className="py-2 pr-3">
                        <span
                          className="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold"
                          style={{
                            color: ok ? "var(--authentic)" : "var(--fake)",
                            backgroundColor: ok ? "var(--authentic-soft)" : "var(--fake-soft)",
                          }}
                        >
                          {f.resultado.veredicto}
                        </span>
                      </td>
                      <td className="num py-2 pr-3 font-medium text-foreground">{pct(f.resultado.probabilidad)}</td>
                      <td className="num py-2 pr-3 text-muted-foreground">
                        {f.resultado.consenso}/{f.resultado.totalModelos}
                      </td>
                      <td className="py-2 pr-3 text-muted-foreground">{f.resultado.confianza}</td>
                      <td className="py-2 pr-3">
                        {f.etiquetaReal ? (
                          <span
                            className="num"
                            style={{ color: acierto ? "var(--authentic)" : "var(--fake)" }}
                          >
                            {f.etiquetaReal}
                          </span>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  )
}
