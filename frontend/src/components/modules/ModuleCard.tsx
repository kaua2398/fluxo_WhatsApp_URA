import { motion } from 'framer-motion'
import { ChevronRight, GitBranch, Link2, Layers } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { Module } from '@/types'
import { cn } from '@/lib/utils'

interface ModuleCardProps {
  module: Module
  isSelected?: boolean
  onClick: () => void
  index?: number
}

export function ModuleCard({ module, isSelected, onClick, index = 0 }: ModuleCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card
        className={cn(
          'cursor-pointer transition-all hover:shadow-md hover:border-[var(--color-primary)]',
          isSelected && 'border-[var(--color-primary)] ring-2 ring-[var(--color-primary)]/20'
        )}
        onClick={onClick}
      >
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-[var(--color-primary)]" />
              <CardTitle className="text-base">{module.name}</CardTitle>
            </div>
            <ChevronRight className="h-4 w-4 text-[var(--color-muted-foreground)]" />
          </div>
          <CardDescription className="line-clamp-2">{module.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 text-xs text-[var(--color-muted-foreground)]">
            <span className="flex items-center gap-1">
              <GitBranch className="h-3 w-3" />
              {module.node_count} estados
            </span>
            <span className="flex items-center gap-1">
              <Link2 className="h-3 w-3" />
              {module.api_count} APIs
            </span>
            <span className="flex items-center gap-1">
              ⚡ {module.decision_count} decisões
            </span>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
