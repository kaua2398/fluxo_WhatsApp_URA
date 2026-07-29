import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { GitCompare, Plus, Minus, Edit } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/lib/api'
import type { Version } from '@/types'

interface ComparisonPanelProps {
  flowId: string
}

export function ComparisonPanel({ flowId }: ComparisonPanelProps) {
  const [versionA, setVersionA] = useState<number | null>(null)
  const [versionB, setVersionB] = useState<number | null>(null)

  const { data: versions = [] } = useQuery({
    queryKey: ['versions', flowId],
    queryFn: () => api.versions.list(flowId),
    enabled: !!flowId,
  })

  const { data: comparison, refetch, isFetching } = useQuery({
    queryKey: ['comparison', flowId, versionA, versionB],
    queryFn: () => api.versions.compare(flowId, versionA!, versionB!),
    enabled: !!flowId && versionA !== null && versionB !== null,
  })

  return (
    <div className="p-6">
      <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
        <GitCompare className="h-5 w-5" />
        Comparar Versões
      </h2>

      <div className="flex gap-4 mb-6">
        <div>
          <label className="text-xs text-[var(--color-muted-foreground)] block mb-1">Versão A</label>
          <select
            className="h-9 rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px-2 text-sm"
            value={versionA ?? ''}
            onChange={(e) => setVersionA(Number(e.target.value) || null)}
          >
            <option value="">Selecionar...</option>
            {versions.map((v: Version) => (
              <option key={v.id} value={v.version_number}>v{v.version_number} {v.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-[var(--color-muted-foreground)] block mb-1">Versão B</label>
          <select
            className="h-9 rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px-2 text-sm"
            value={versionB ?? ''}
            onChange={(e) => setVersionB(Number(e.target.value) || null)}
          >
            <option value="">Selecionar...</option>
            {versions.map((v: Version) => (
              <option key={v.id} value={v.version_number}>v{v.version_number} {v.label}</option>
            ))}
          </select>
        </div>
        <div className="flex items-end">
          <Button
            onClick={() => refetch()}
            disabled={!versionA || !versionB || isFetching}
          >
            Comparar
          </Button>
        </div>
      </div>

      {comparison && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ChangeCard
            title="Adicionados"
            icon={<Plus className="h-4 w-4 text-green-600" />}
            items={comparison.added_nodes.map((n) => String(n.label ?? n.external_id))}
            color="green"
          />
          <ChangeCard
            title="Removidos"
            icon={<Minus className="h-4 w-4 text-red-600" />}
            items={comparison.removed_nodes.map((n) => String(n.label ?? n.external_id))}
            color="red"
          />
          <ChangeCard
            title="Alterados"
            icon={<Edit className="h-4 w-4 text-amber-600" />}
            items={comparison.changed_nodes.map(
              (c) => `${String(c.before.label)} → ${String(c.after.label)}`
            )}
            color="amber"
          />
        </div>
      )}

      {versions.length < 2 && (
        <p className="text-sm text-[var(--color-muted-foreground)]">
          São necessárias pelo menos 2 versões para comparar. Faça upload de uma nova versão do fluxo.
        </p>
      )}
    </div>
  )
}

function ChangeCard({
  title,
  icon,
  items,
  color,
}: {
  title: string
  icon: React.ReactNode
  items: string[]
  color: string
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            {icon}
            {title} ({items.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="text-sm space-y-1 max-h-48 overflow-y-auto">
            {items.length === 0 ? (
              <li className="text-[var(--color-muted-foreground)]">Nenhum</li>
            ) : (
              items.map((item, i) => (
                <li key={i} className="truncate">{item}</li>
              ))
            )}
          </ul>
        </CardContent>
      </Card>
    </motion.div>
  )
}
