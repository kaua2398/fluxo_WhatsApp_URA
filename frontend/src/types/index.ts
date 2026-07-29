export interface Project {
  id: string
  name: string
  description: string | null
  flow_count: number
  created_at: string
  updated_at: string
}

export interface Flow {
  id: string
  project_id: string
  name: string
  flow_type: string
  description: string | null
  source_type: string | null
  source_file: string | null
  is_active: boolean
  node_count: number
  api_count: number
  decision_count: number
  version_count: number
  created_at: string
  updated_at: string
}

export interface FlowNode {
  id: string
  external_id: string
  label: string
  node_type: string
  description: string | null
  module: string | null
  position_x: number
  position_y: number
  metadata: Record<string, unknown> | null
  is_collapsed: boolean
}

export interface FlowEdge {
  id: string
  source_id: string
  target_id: string
  label: string | null
  edge_type: string
  metadata: Record<string, unknown> | null
}

export interface FlowApi {
  id: string
  external_id: string
  name: string
  method: string
  url: string | null
  description: string | null
  node_ids: string[] | null
  metadata: Record<string, unknown> | null
}

export interface FlowVariable {
  id: string
  external_id: string
  name: string
  description: string | null
  default_value: string | null
  node_ids: string[] | null
  metadata: Record<string, unknown> | null
}

export interface FlowDetail extends Flow {
  nodes: FlowNode[]
  edges: FlowEdge[]
  apis: FlowApi[]
  variables: FlowVariable[]
}

export interface Module {
  id: string
  name: string
  description: string
  node_count: number
  api_count: number
  decision_count: number
  nodes: FlowNode[]
}

export interface Version {
  id: string
  flow_id: string
  version_number: number
  label: string | null
  created_at: string
}

export interface Documentation {
  flow_id: string
  summary: string
  objective: string
  inputs: string
  outputs: string
  apis: string
  variables: string
  flow_description: string
  rules: string
  exceptions: string
}

export interface ComparisonResult {
  flow_id: string
  version_a: number
  version_b: number
  added_nodes: Record<string, unknown>[]
  removed_nodes: Record<string, unknown>[]
  changed_nodes: { before: Record<string, unknown>; after: Record<string, unknown> }[]
  added_edges: Record<string, unknown>[]
  removed_edges: Record<string, unknown>[]
}

export interface SearchResult {
  type: string
  id: string
  label: string
  module?: string | null
  flow_id?: string | null
}

export interface UploadResult {
  flow_id: string
  filename: string
  source_type: string
  node_count: number
  edge_count: number
  module_count: number
  version_number: number
}

export interface ExportResult {
  id: string
  flow_id: string
  format: string
  file_path: string
  download_url: string
  created_at: string
}

export type FlowType = 'whatsapp' | 'ura' | 'commercial' | 'email' | 'generic'

export const FLOW_TYPE_ICONS: Record<string, string> = {
  whatsapp: '📱',
  ura: '☎',
  commercial: '🤖',
  email: '📧',
  generic: '📋',
}

export const NODE_TYPE_COLORS: Record<string, string> = {
  start: '#22c55e',
  end: '#ef4444',
  menu: '#6366f1',
  submenu: '#818cf8',
  message: '#3b82f6',
  condition: '#f59e0b',
  api: '#8b5cf6',
  variable: '#06b6d4',
  human_handoff: '#ec4899',
  error: '#dc2626',
  flow: '#14b8a6',
  module: '#64748b',
  unknown: '#94a3b8',
}
