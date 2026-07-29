import { memo } from 'react'
import { Handle, Position, type NodeProps } from '@xyflow/react'
import { NODE_TYPE_COLORS } from '@/types'
import { getNodeTypeLabel } from '@/lib/utils'
import { cn } from '@/lib/utils'

export interface FlowNodeData {
  label: string
  nodeType: string
  description?: string | null
  module?: string | null
  isCollapsed?: boolean
  onToggle?: () => void
}

function FlowNodeComponent({ data, selected }: NodeProps & { data: FlowNodeData }) {
  const color = NODE_TYPE_COLORS[data.nodeType] ?? NODE_TYPE_COLORS.unknown

  return (
    <div
      className={cn(
        'min-w-[160px] max-w-[220px] rounded-lg border-2 bg-[var(--color-card)] shadow-md transition-all',
        selected && 'ring-2 ring-[var(--color-ring)] ring-offset-2'
      )}
      style={{ borderColor: color }}
    >
      <Handle type="target" position={Position.Top} className="!bg-[var(--color-muted-foreground)] !w-2 !h-2" />
      <div className="px-3 py-2">
        <div className="flex items-center gap-2 mb-1">
          <span
            className="inline-block w-2 h-2 rounded-full shrink-0"
            style={{ backgroundColor: color }}
          />
          <span className="text-[10px] uppercase tracking-wide text-[var(--color-muted-foreground)]">
            {getNodeTypeLabel(data.nodeType)}
          </span>
        </div>
        <p className="text-sm font-medium leading-tight line-clamp-2">{data.label}</p>
        {data.description && (
          <p className="text-xs text-[var(--color-muted-foreground)] mt-1 line-clamp-2">{data.description}</p>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-[var(--color-muted-foreground)] !w-2 !h-2" />
    </div>
  )
}

export default memo(FlowNodeComponent)
