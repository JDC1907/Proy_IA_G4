import { TreeDeciduous, TrendingUp, Sigma, BrainCircuit, Trees } from "lucide-react"

const MAP = {
  tree: TreeDeciduous,
  boosting: TrendingUp,
  logistic: Sigma,
  mlp: BrainCircuit,
  forest: Trees,
} as const

export function ModelIcon({ icono, className }: { icono: string; className?: string }) {
  const Icon = MAP[icono as keyof typeof MAP] ?? Sigma
  return <Icon className={className} strokeWidth={1.8} aria-hidden />
}
