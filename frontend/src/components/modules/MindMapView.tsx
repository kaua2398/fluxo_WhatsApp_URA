import { motion } from 'framer-motion'
import { ArrowDown } from 'lucide-react'
import { getFlowTypeIcon } from '@/lib/utils'
import type { Module } from '@/types'

interface MindMapViewProps {
  flowName: string
  flowType: string
  modules: Module[]
  onModuleClick: (module: Module) => void
}

export function MindMapView({ flowName, flowType, modules, onModuleClick }: MindMapViewProps) {
  const sortedModules = [...modules].sort((a, b) => a.name.localeCompare(b.name))

  return (
    <div className="flex flex-col items-center py-8 px-4 min-h-full">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex flex-col items-center"
      >
        <div className="bg-[var(--color-primary)] text-[var(--color-primary-foreground)] rounded-2xl px-6 py-3 text-lg font-semibold shadow-lg">
          {getFlowTypeIcon(flowType)} {flowName}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="my-4"
        >
          <ArrowDown className="h-6 w-6 text-[var(--color-muted-foreground)]" />
        </motion.div>

        <div className="text-sm text-[var(--color-muted-foreground)] mb-6">Usuário</div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mb-4"
        >
          <ArrowDown className="h-6 w-6 text-[var(--color-muted-foreground)]" />
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 w-full max-w-6xl">
          {sortedModules.map((module, index) => (
            <motion.button
              key={module.id}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index + 0.4 }}
              whileHover={{ scale: 1.03, y: -2 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => onModuleClick(module)}
              className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl p-4 text-left shadow-sm hover:shadow-md hover:border-[var(--color-primary)] transition-all cursor-pointer"
            >
              <h3 className="font-semibold text-base mb-1">{module.name}</h3>
              <p className="text-xs text-[var(--color-muted-foreground)] mb-3 line-clamp-2">
                {module.description}
              </p>
              <div className="flex gap-3 text-xs text-[var(--color-muted-foreground)]">
                <span>{module.node_count} estados</span>
                <span>{module.api_count} APIs</span>
                <span>{module.decision_count} decisões</span>
              </div>
            </motion.button>
          ))}
        </div>

        {sortedModules.length === 0 && (
          <p className="text-[var(--color-muted-foreground)] text-center mt-8">
            Nenhum módulo detectado. Faça upload de um arquivo para começar.
          </p>
        )}
      </motion.div>
    </div>
  )
}
