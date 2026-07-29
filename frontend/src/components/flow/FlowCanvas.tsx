import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Panel,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  type NodeTypes,
  BackgroundVariant,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { motion, AnimatePresence } from 'framer-motion'
import { Maximize2, Search, ZoomIn } from 'lucide-react'
import FlowNodeComponent, { type FlowNodeData } from './FlowNode'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { NODE_TYPE_COLORS, type FlowNode, type FlowEdge } from '@/types'
import { api } from '@/lib/api'
import { useAppStore } from '@/stores/appStore'

const nodeTypes: NodeTypes = {
  flowNode: FlowNodeComponent,
}

interface FlowCanvasProps {
  nodes: FlowNode[]
  edges: FlowEdge[]
  flowId: string
  moduleFilter?: string | null
  onNodeClick?: (node: FlowNode) => void
}

export function FlowCanvas({ nodes, edges, flowId, moduleFilter, onNodeClick }: FlowCanvasProps) {
  const [search, setSearch] = useState('')
  const [highlightedIds, setHighlightedIds] = useState<Set<string>>(new Set())
  const searchQuery = useAppStore((s) => s.searchQuery)

  const filteredNodes = useMemo(() => {
    let result = nodes
    if (moduleFilter) {
      result = result.filter((n) => (n.module ?? 'Geral') === moduleFilter)
    }
    return result
  }, [nodes, moduleFilter])

  const filteredNodeIds = useMemo(() => new Set(filteredNodes.map((n) => n.id)), [filteredNodes])

  const initialNodes: Node<FlowNodeData>[] = useMemo(
    () =>
      filteredNodes.map((n) => ({
        id: n.id,
        type: 'flowNode',
        position: { x: n.position_x, y: n.position_y },
        data: {
          label: n.label,
          nodeType: n.node_type,
          description: n.description,
          module: n.module,
        },
      })),
    [filteredNodes]
  )

  const initialEdges: Edge[] = useMemo(
    () =>
      edges
        .filter((e) => filteredNodeIds.has(e.source_id) && filteredNodeIds.has(e.target_id))
        .map((e) => ({
          id: e.id,
          source: e.source_id,
          target: e.target_id,
          label: e.label ?? undefined,
          animated: e.edge_type === 'condition_true',
          style: {
            stroke: e.edge_type === 'error' ? '#dc2626' : e.edge_type === 'condition_false' ? '#f59e0b' : '#94a3b8',
          },
        })),
    [edges, filteredNodeIds]
  )

  const [rfNodes, setRfNodes, onNodesChange] = useNodesState(initialNodes)
  const [rfEdges, setRfEdges, onEdgesChange] = useEdgesState(initialEdges)

  useEffect(() => {
    setRfNodes(initialNodes)
    setRfEdges(initialEdges)
  }, [initialNodes, initialEdges, setRfNodes, setRfEdges])

  useEffect(() => {
    const query = search || searchQuery
    if (!query) {
      setHighlightedIds(new Set())
      return
    }
    api.search(flowId, query).then((results) => {
      setHighlightedIds(new Set(results.map((r) => r.id)))
    }).catch(() => setHighlightedIds(new Set()))
  }, [search, searchQuery, flowId])

  const onNodeDragStop = useCallback(
    (_: React.MouseEvent, node: Node) => {
      api.nodes.updatePosition(node.id, node.position.x, node.position.y).catch(console.error)
    },
    []
  )

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const original = nodes.find((n) => n.id === node.id)
      if (original && onNodeClick) onNodeClick(original)
    },
    [nodes, onNodeClick]
  )

  return (
    <div className="h-full w-full relative">
      <ReactFlow
        nodes={rfNodes.map((n) => ({
          ...n,
          style: highlightedIds.has(n.id)
            ? { boxShadow: '0 0 0 3px var(--color-primary)', borderRadius: 8 }
            : undefined,
        }))}
        edges={rfEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeDragStop={onNodeDragStop}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
        <Controls showInteractive={false} />
        <MiniMap
          nodeColor={(n) => NODE_TYPE_COLORS[(n.data as FlowNodeData)?.nodeType] ?? '#94a3b8'}
          maskColor="rgba(0,0,0,0.08)"
          className="!bg-[var(--color-card)] !border-[var(--color-border)]"
        />
        <Panel position="top-right" className="flex gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--color-muted-foreground)]" />
            <Input
              placeholder="Pesquisar nós..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 w-48 bg-[var(--color-card)]"
            />
          </div>
        </Panel>
        <AnimatePresence>
          {moduleFilter && (
            <Panel position="top-left">
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm shadow-sm"
              >
                <span className="text-[var(--color-muted-foreground)]">Módulo: </span>
                <strong>{moduleFilter}</strong>
              </motion.div>
            </Panel>
          )}
        </AnimatePresence>
      </ReactFlow>
    </div>
  )
}
