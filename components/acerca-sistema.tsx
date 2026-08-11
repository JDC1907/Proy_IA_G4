import { Info, Database, Cpu, BookOpen } from "lucide-react"

const METRICAS = [
  { modelo: "Random Forest", umbral: 0.5233, acc: 0.9027, f1: 0.8956, auc: 0.9619 },
  { modelo: "Gradient Boosting", umbral: 0.4929, acc: 0.9014, f1: 0.8955, auc: 0.9624, principal: true },
  { modelo: "Red Neuronal MLP", umbral: 0.4586, acc: 0.8984, f1: 0.893, auc: 0.9607 },
  { modelo: "Árbol de Decisión", umbral: 0.4684, acc: 0.8905, f1: 0.8837, auc: 0.9462 },
  { modelo: "Regresión Logística", umbral: 0.4706, acc: 0.8462, f1: 0.8461, auc: 0.9221 },
]

export function AcercaSistema() {
  return (
    <div className="flex flex-col gap-4">
      <section className="rounded-xl border border-border bg-card p-6">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-foreground">
          <Info className="h-5 w-5 text-primary" strokeWidth={1.8} aria-hidden />
          Sistema de clasificación de cuentas de Instagram
        </h2>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-muted-foreground">
          Clasifica una cuenta como <strong className="text-foreground">auténtica</strong> o{" "}
          <strong className="text-foreground">falsa</strong> a partir de 17 atributos públicos de perfil,
          comportamiento y engagement, usando modelos de aprendizaje automático supervisado entrenados sobre el
          conjunto de Purba, Asirvatham y Murugesan (IJECE, 2020).
        </p>

        <div className="mt-5 grid gap-3 sm:grid-cols-3">
          <Tarjeta Icon={Database} titulo="Dataset" texto="64 244 cuentas tras limpieza · 51 395 entrenamiento / 12 849 prueba · estratificado." />
          <Tarjeta Icon={Cpu} titulo="Modelo principal" texto="Gradient Boosting (umbral 0.4929): menos falsos negativos y decisiones explicables." />
          <Tarjeta Icon={BookOpen} titulo="Explicabilidad" texto="Cada decisión individual se explica con la contribución de cada atributo (SHAP)." />
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card p-6">
        <h3 className="font-semibold text-foreground">Desempeño de los modelos (conjunto de prueba)</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          Métricas con el umbral óptimo ajustado para maximizar el F1 sobre la clase falsa.
        </p>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted-foreground">
                <th className="py-2 pr-3 font-medium">Modelo</th>
                <th className="py-2 pr-3 font-medium">Umbral</th>
                <th className="py-2 pr-3 font-medium">Accuracy</th>
                <th className="py-2 pr-3 font-medium">F1 (falsa)</th>
                <th className="py-2 pr-3 font-medium">AUC-ROC</th>
              </tr>
            </thead>
            <tbody>
              {METRICAS.map((m) => (
                <tr key={m.modelo} className="border-b border-border/60">
                  <td className="py-2 pr-3 font-medium text-foreground">
                    {m.modelo}
                    {m.principal && (
                      <span className="ml-2 rounded bg-primary-soft px-1.5 py-0.5 text-[11px] font-semibold text-primary">
                        principal
                      </span>
                    )}
                  </td>
                  <td className="num py-2 pr-3 text-muted-foreground">{m.umbral.toFixed(4)}</td>
                  <td className="num py-2 pr-3 text-foreground">{(m.acc * 100).toFixed(2)}%</td>
                  <td className="num py-2 pr-3 text-foreground">{(m.f1 * 100).toFixed(2)}%</td>
                  <td className="num py-2 pr-3 text-foreground">{(m.auc * 100).toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card p-6">
        <h3 className="font-semibold text-foreground">Cómo leer el resultado</h3>
        <ul className="mt-2 flex list-disc flex-col gap-2 pl-5 text-sm leading-relaxed text-muted-foreground">
          <li>
            El puntaje es la <strong className="text-foreground">probabilidad de autenticidad</strong>. Se compara
            contra el umbral del modelo (no el 0.5 por defecto).
          </li>
          <li>
            El <strong className="text-foreground">nivel de confianza</strong> mide la distancia entre el puntaje y el
            umbral. Confianza baja significa que la cuenta cae en una zona ambigua y conviene revisarla manualmente.
          </li>
          <li>
            El panel de señales indica cuánto empujó cada atributo hacia cada clase{" "}
            <strong className="text-foreground">para esa cuenta</strong>, no en promedio.
          </li>
          <li>
            <strong className="text-foreground">Limitación declarada:</strong> el conjunto de entrenamiento es de 2020;
            valores muy por encima de los máximos observados son extrapolaciones.
          </li>
        </ul>
        <p className="mt-4 text-xs text-muted-foreground">
          Grupo N.4 — CCPG1044 Inteligencia Artificial — ESPOL
        </p>
      </section>
    </div>
  )
}

function Tarjeta({ Icon, titulo, texto }: { Icon: typeof Info; titulo: string; texto: string }) {
  return (
    <div className="rounded-lg border border-border p-4">
      <div className="flex items-center gap-2 text-primary">
        <Icon className="h-4.5 w-4.5" strokeWidth={1.8} aria-hidden />
        <span className="text-sm font-semibold text-foreground">{titulo}</span>
      </div>
      <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">{texto}</p>
    </div>
  )
}
