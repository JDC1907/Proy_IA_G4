"use client"

import { useState } from "react"
import {
  PencilLine,
  ChevronDown,
  Sparkles,
  FileUp,
  Activity,
  Users2,
  UserRound,
  Zap,
  FileText,
  ShieldQuestion,
} from "lucide-react"
import { GRUPOS, ATRIBUTOS, type ValoresCuenta, type ClaveAtributo } from "@/lib/atributos"

const ICONOS_GRUPO = [Activity, Users2, UserRound, Zap, FileText, ShieldQuestion]

export function FormularioManual({
  valores,
  onChange,
  onAnalizar,
  onIrArchivo,
}: {
  valores: ValoresCuenta
  onChange: (clave: ClaveAtributo, valor: number) => void
  onAnalizar: () => void
  onIrArchivo: () => void
}) {
  const [abierto, setAbierto] = useState<number | null>(null)

  return (
    <section className="rounded-xl border border-border bg-card p-5">
      <div className="mb-1 flex items-center gap-2">
        <PencilLine className="h-4.5 w-4.5 text-primary" strokeWidth={1.8} aria-hidden />
        <h2 className="font-semibold text-foreground">Ingresar datos manualmente</h2>
      </div>
      <p className="mb-4 text-sm text-muted-foreground">Completa los 17 atributos de la cuenta.</p>

      <div className="flex flex-col gap-2">
        {GRUPOS.map((g, i) => {
          const Icon = ICONOS_GRUPO[i % ICONOS_GRUPO.length]
          const open = abierto === i
          return (
            <div key={g.titulo} className="rounded-lg border border-border">
              <button
                onClick={() => setAbierto(open ? null : i)}
                aria-expanded={open}
                className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left hover:bg-muted/60"
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-md bg-primary-soft text-primary">
                  <Icon className="h-4 w-4" strokeWidth={1.8} aria-hidden />
                </span>
                <span className="flex-1 leading-tight">
                  <span className="block text-sm font-medium text-foreground">
                    {g.titulo} <span className="text-muted-foreground">({g.claves.length})</span>
                  </span>
                  <span className="num block text-xs text-muted-foreground">{g.claves.join(", ")}</span>
                </span>
                <ChevronDown
                  className={`h-4 w-4 text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`}
                  aria-hidden
                />
              </button>
              {open && (
                <div className="grid gap-3 border-t border-border p-3 sm:grid-cols-2">
                  {g.claves.map((clave) => (
                    <Campo key={clave} clave={clave} valor={valores[clave]} onChange={onChange} />
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>

      <button
        onClick={onAnalizar}
        className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground transition-colors hover:opacity-90"
      >
        <Sparkles className="h-4 w-4" strokeWidth={1.8} aria-hidden />
        Analizar cuenta
      </button>

      <p className="mt-3 text-center text-xs text-muted-foreground">
        ¿Tienes muchas cuentas? Analiza un archivo CSV.
      </p>
      <button
        onClick={onIrArchivo}
        className="mt-2 flex w-full items-center justify-center gap-2 rounded-lg border border-border bg-card px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-muted/60"
      >
        <FileUp className="h-4 w-4" strokeWidth={1.8} aria-hidden />
        Ir a Analizar un archivo
      </button>
    </section>
  )
}

function Campo({
  clave,
  valor,
  onChange,
}: {
  clave: ClaveAtributo
  valor: number
  onChange: (clave: ClaveAtributo, valor: number) => void
}) {
  const at = ATRIBUTOS[clave]

  if (at.tipo === "binario") {
    return (
      <label className="flex flex-col gap-1">
        <span className="num text-xs font-medium text-foreground" title={at.descripcion}>
          {clave} <span className="font-normal text-muted-foreground">· {at.etiqueta}</span>
        </span>
        <select
          value={valor >= 0.5 ? "1" : "0"}
          onChange={(e) => onChange(clave, Number(e.target.value))}
          className="rounded-md border border-input bg-card px-2 py-1.5 text-sm text-foreground outline-none focus:border-ring focus:ring-2 focus:ring-ring/30"
        >
          <option value="1">Sí</option>
          <option value="0">No</option>
        </select>
      </label>
    )
  }

  const step = at.tipo === "entero" ? 1 : at.tipo === "proporcion" ? 0.01 : 0.01
  return (
    <label className="flex flex-col gap-1">
      <span className="num text-xs font-medium text-foreground" title={at.descripcion}>
        {clave} <span className="font-normal text-muted-foreground">· {at.etiqueta}</span>
      </span>
      <input
        type="number"
        inputMode="decimal"
        step={step}
        min={0}
        max={at.tipo === "proporcion" ? 1 : undefined}
        value={Number.isFinite(valor) ? valor : 0}
        onChange={(e) => onChange(clave, e.target.value === "" ? 0 : Number(e.target.value))}
        className="num rounded-md border border-input bg-card px-2 py-1.5 text-sm text-foreground outline-none focus:border-ring focus:ring-2 focus:ring-ring/30"
      />
    </label>
  )
}
