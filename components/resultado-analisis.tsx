"use client"

import { Sparkles, ShieldCheck, Ghost, HelpCircle } from "lucide-react"
import type { Resultado } from "@/lib/clasificador"
import { pct } from "@/lib/formato"

export function ResultadoAnalisis({ r }: { r: Resultado }) {
  const autentica = r.veredicto === "AUTÉNTICA"
  const dudoso = r.confianza === "BAJA"
  const tono = dudoso ? "ambiguous" : autentica ? "authentic" : "fake"
  const color = `var(--${tono})`
  const soft = `var(--${tono}-soft)`
  const Icon = dudoso ? HelpCircle : autentica ? ShieldCheck : Ghost

  const posicion = Math.min(100, Math.max(0, r.probabilidad * 100))
  const evidencia =
    r.confianza === "ALTA"
      ? "Evidencia alta"
      : r.confianza === "MEDIA"
        ? "Evidencia media"
        : "Evidencia baja"
  const evidenciaTexto =
    r.confianza === "BAJA"
      ? "Las señales no son concluyentes; se recomienda revisión manual."
      : autentica
        ? "Los modelos coinciden en que esta cuenta es auténtica."
        : "Los modelos coinciden en que esta cuenta es falsa."

  return (
    <section className="rounded-xl border border-border bg-card p-5">
      <div className="mb-5 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-soft text-primary">
          <Sparkles className="h-5 w-5" strokeWidth={1.8} aria-hidden />
        </div>
        <div>
          <h2 className="font-semibold text-foreground">Resultado del análisis</h2>
          <p className="text-sm text-muted-foreground">Basado en 5 modelos de aprendizaje automático</p>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Veredicto */}
        <div className="rounded-lg border border-border p-5">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
                Veredicto final
              </div>
              <div className="mt-1 text-3xl font-extrabold tracking-tight" style={{ color }}>
                CUENTA {r.veredicto}
              </div>
            </div>
            <span
              className="flex h-12 w-12 items-center justify-center rounded-full"
              style={{ backgroundColor: soft, color }}
            >
              <Icon className="h-6 w-6" strokeWidth={2} aria-hidden />
            </span>
          </div>

          <div
            className="mt-4 flex items-start gap-2 rounded-lg p-3"
            style={{ backgroundColor: soft }}
          >
            <Icon className="mt-0.5 h-4 w-4 shrink-0" style={{ color }} strokeWidth={2} aria-hidden />
            <div>
              <div className="text-sm font-semibold" style={{ color }}>
                {evidencia}
              </div>
              <div className="text-xs text-foreground/70">{evidenciaTexto}</div>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-3 gap-3">
            <Metrica etiqueta="Probabilidad de autenticidad" valor={pct(r.probabilidad)} color={color} />
            <Metrica etiqueta="Umbral de decisión" valor={pct(r.umbral)} />
            <Metrica etiqueta="Incertidumbre (margen)" valor={`±${pct(r.margen)}`} />
          </div>
        </div>

        {/* Puntaje del modelo */}
        <div className="rounded-lg border border-border p-5">
          <div className="mb-8 text-sm font-medium text-foreground">
            Puntaje del modelo{" "}
            <span className="font-normal text-muted-foreground">(más a la derecha = más auténtica)</span>
          </div>

          <div className="relative mb-2">
            {/* burbuja */}
            <div
              className="absolute -top-8 z-10 -translate-x-1/2 whitespace-nowrap rounded-md px-2 py-1 text-xs font-semibold text-white"
              style={{ left: `${posicion}%`, backgroundColor: "var(--primary)" }}
            >
              {pct(r.probabilidad)}
            </div>
            {/* barra gradiente */}
            <div
              className="h-2.5 w-full rounded-full"
              style={{
                background:
                  "linear-gradient(90deg, #e15b5b 0%, #e7c95b 48%, #63c48c 68%, #16a06a 100%)",
              }}
            />
            {/* tick umbral */}
            <div className="absolute top-1/2 h-4 w-px -translate-y-1/2 bg-foreground/30" style={{ left: "50%" }} />
            {/* marcador */}
            <div
              className="absolute top-1/2 h-5 w-5 -translate-x-1/2 -translate-y-1/2 rounded-full border-4 border-white bg-foreground shadow-md"
              style={{ left: `${posicion}%` }}
            />
          </div>

          <div className="flex justify-between text-xs text-muted-foreground">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
          <div className="mt-2 flex justify-between text-xs">
            <span className="text-transparent">.</span>
            <span className="text-center font-medium text-muted-foreground">
              Umbral
              <br />
              50%
            </span>
            <span className="text-right font-medium text-foreground">
              Puntaje actual
            </span>
          </div>

          {/* Segmentos */}
          <div className="mt-5 grid grid-cols-3 overflow-hidden rounded-lg border border-border text-center text-xs">
            <div className="bg-fake-soft/60 px-2 py-2 font-medium text-fake">Hacia FALSA</div>
            <div className="border-x border-border bg-primary-soft/60 px-2 py-2 font-medium text-primary">
              Zona de incertidumbre
              <br />
              <span className="text-[11px] text-muted-foreground">±{pct(r.margen)}</span>
            </div>
            <div className="bg-authentic-soft/60 px-2 py-2 font-medium text-authentic">Hacia AUTÉNTICA</div>
          </div>
        </div>
      </div>
    </section>
  )
}

function Metrica({ etiqueta, valor, color }: { etiqueta: string; valor: string; color?: string }) {
  return (
    <div>
      <div className="text-[11px] leading-tight text-muted-foreground">{etiqueta}</div>
      <div className="num mt-1 text-xl font-bold" style={{ color: color ?? "var(--foreground)" }}>
        {valor}
      </div>
    </div>
  )
}
