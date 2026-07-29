import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { getNodeTypeLabel } from '@/lib/utils'
import { NODE_TYPE_COLORS, type FlowNode, type FlowApi, type FlowVariable } from '@/types'

interface DetailPanelProps {
  node?: FlowNode | null
  api?: FlowApi | null
  variable?: FlowVariable | null
  onClose: () => void
}

export function DetailPanel({ node, api, variable, onClose }: DetailPanelProps) {
  const isOpen = !!(node || api || variable)

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ x: 300, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 300, opacity: 0 }}
          transition={{ type: 'spring', damping: 25 }}
          className="absolute right-0 top-0 bottom-0 w-80 bg-[var(--color-card)] border-l border-[var(--color-border)] shadow-xl z-10 flex flex-col"
        >
          <div className="flex items-center justify-between p-4 border-b border-[var(--color-border)]">
            <h3 className="font-semibold">Detalhes</h3>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>

          <div className="p-4 flex-1 overflow-y-auto space-y-4">
            {node && (
              <>
                <div>
                  <span
                    className="inline-block px-2 py-0.5 rounded text-xs text-white mb-2"
                    style={{ backgroundColor: NODE_TYPE_COLORS[node.node_type] }}
                  >
                    {getNodeTypeLabel(node.node_type)}
                  </span>
                  <h4 className="font-medium text-lg">{node.label}</h4>
                  {node.description && (
                    <p className="text-sm text-[var(--color-muted-foreground)] mt-1">{node.description}</p>
                  )}
                </div>
                <div className="text-sm space-y-2">
                  <div><span className="text-[var(--color-muted-foreground)]">ID:</span> {node.external_id}</div>
                  {node.module && (
                    <div><span className="text-[var(--color-muted-foreground)]">Módulo:</span> {node.module}</div>
                  )}
                </div>
                {node.metadata && Object.keys(node.metadata).length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium mb-2">Metadados</h5>
                    <pre className="text-xs bg-[var(--color-muted)] p-2 rounded overflow-x-auto">
                      {JSON.stringify(node.metadata, null, 2)}
                    </pre>
                  </div>
                )}
              </>
            )}

            {api && (
              <>
                <h4 className="font-medium text-lg">{api.name}</h4>
                <div className="text-sm space-y-2">
                  <div><span className="text-[var(--color-muted-foreground)]">Método:</span> {api.method}</div>
                  {api.url && (
                    <div><span className="text-[var(--color-muted-foreground)]">URL:</span> <code className="text-xs">{api.url}</code></div>
                  )}
                  {api.description && <p className="text-[var(--color-muted-foreground)]">{api.description}</p>}
                  {api.node_ids && (
                    <div><span className="text-[var(--color-muted-foreground)]">Usado em:</span> {api.node_ids.length} nó(s)</div>
                  )}
                </div>
              </>
            )}

            {variable && (
              <>
                <h4 className="font-medium text-lg">{variable.name}</h4>
                <div className="text-sm space-y-2">
                  {variable.default_value && (
                    <div><span className="text-[var(--color-muted-foreground)]">Padrão:</span> {variable.default_value}</div>
                  )}
                  {variable.description && <p className="text-[var(--color-muted-foreground)]">{variable.description}</p>}
                  {variable.node_ids && (
                    <div>
                      <span className="text-[var(--color-muted-foreground)]">Utilizada em {variable.node_ids.length} nó(s)</span>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
