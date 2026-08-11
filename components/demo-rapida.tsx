"use client"

import { Zap, Ghost, ShieldCheck, HelpCircle } from "lucide-react"
import type { Ejemplo } from "@/lib/ejemplos"

const CARDS: {
  tipo: Ejemplo["tipo"]
  titulo: string
  sub: string
  Icon: typeof Ghost
  tono: "fake" | "authentic" | "ambiguous"
}[] = [
  { tipo: "falsa", titulo: "Cuenta falsa clara", sub: "Ejemplo de cuenta falsa", Icon: Ghost, tono: "fake" },
  { tipo: "autentica", titulo: "Cuenta auténtica clara", sub: "Ejemplo de cuenta auténtica", Icon: ShieldCheck, tono: "authentic" },
  { tipo: "dudosa", titulo: "Caso ambiguo", sub: "Ejemplo de caso dudoso", Icon: HelpCircle, tono: "ambiguous" },
]

const TONO = {
  fake: "border-fake/25 bg-fake-soft/60 hover:border-fake/50 [--ic:var(--fake)] [--ic-bg:var(--fake-soft)]",
  authentic: "border-authentic/25 bg-authentic-soft/60 hover:border-authentic/50 [--ic:var(--authentic)] [--ic-bg:var(--authentic-soft)]",
  ambiguous: "border-ambiguous/25 bg-ambiguous-soft/60 hover:border-ambiguous/50 [--ic:var(--ambiguous)] [--ic-bg:var(--ambiguous-soft)]",
}

export function DemoRapida({ onElegir }: { onElegir: (tipo: Ejemplo["tipo"]) => void }) {
  return (
    <section className="rounded-xl border border-border bg-card p-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center">
        <div className="flex items-start gap-3 lg:w-52 lg:shrink-0">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-soft text-primary">
            <Zap className="h-5 w-5" strokeWidth={1.8} aria-hidden />
          </div>
          <div>
            <h2 className="font-semibold text-foreground">Demo rápida</h2>
            <p className="text-sm text-muted-foreground">Prueba ejemplos típicos con un clic</p>
          </div>
        </div>
        <div className="grid flex-1 gap-3 sm:grid-cols-3">
          {CARDS.map(({ tipo, titulo, sub, Icon, tono }) => (
            <button
              key={tipo}
              onClick={() => onElegir(tipo)}
              className={`flex items-center gap-3 rounded-lg border p-3 text-left transition-colors ${TONO[tono]}`}
            >
              <span
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full"
                style={{ backgroundColor: "var(--ic-bg)", color: "var(--ic)" }}
              >
                <Icon className="h-5 w-5" strokeWidth={1.8} aria-hidden />
              </span>
              <span className="leading-tight">
                <span className="block text-sm font-semibold text-foreground">{titulo}</span>
                <span className="block text-xs text-muted-foreground">{sub}</span>
              </span>
            </button>
          ))}
        </div>
      </div>
    </section>
  )
}
