import { useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  ChevronLeft,
  ChevronRight,
  Download,
  FileText,
  FolderOpen,
  GitCompare,
  Moon,
  Search,
  Sun,
  Upload,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { api } from '@/lib/api'
import { getFlowTypeIcon } from '@/lib/utils'
import { useAppStore } from '@/stores/appStore'

interface SidebarProps {
  activeTab: string
  onTabChange: (tab: string) => void
}

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const {
    sidebarOpen,
    setSidebarOpen,
    theme,
    toggleTheme,
    selectedProjectId,
    setSelectedProjectId,
    selectedFlowId,
    setSelectedFlowId,
    searchQuery,
    setSearchQuery,
  } = useAppStore()

  const { data: projects = [] } = useQuery({
    queryKey: ['projects'],
    queryFn: api.projects.list,
  })

  const { data: flows = [] } = useQuery({
    queryKey: ['flows', selectedProjectId],
    queryFn: () => (selectedProjectId ? api.flows.list(selectedProjectId) : Promise.resolve([])),
    enabled: !!selectedProjectId,
  })

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !selectedProjectId) return

    const flowType = file.name.endsWith('.pdf') ? 'ura' : 'whatsapp'
    try {
      const result = await api.upload(selectedProjectId, file, flowType)
      setSelectedFlowId(result.flow_id)
    } catch (err) {
      console.error(err)
    }
    e.target.value = ''
  }

  const navItems = [
    { id: 'flows', label: 'Fluxos', icon: FolderOpen },
    { id: 'search', label: 'Pesquisa', icon: Search },
    { id: 'docs', label: 'Documentação', icon: FileText },
    { id: 'downloads', label: 'Downloads', icon: Download },
    { id: 'versions', label: 'Versões', icon: GitCompare },
  ]

  if (!sidebarOpen) {
    return (
      <div className="w-12 border-r border-[var(--color-border)] bg-[var(--color-sidebar)] flex flex-col items-center py-4 gap-2">
        <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(true)}>
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    )
  }

  return (
    <motion.aside
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-72 border-r border-[var(--color-border)] bg-[var(--color-sidebar)] flex flex-col h-full shrink-0"
    >
      <div className="p-4 border-b border-[var(--color-border)] flex items-center justify-between">
        <div>
          <h1 className="font-bold text-lg tracking-tight">Flow Navigator</h1>
          <p className="text-xs text-[var(--color-muted-foreground)]">Navegador de Fluxos</p>
        </div>
        <div className="flex gap-1">
          <Button variant="ghost" size="icon" onClick={toggleTheme}>
            {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
          </Button>
          <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(false)}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="p-3 border-b border-[var(--color-border)]">
        <label className="text-xs font-medium text-[var(--color-muted-foreground)] mb-1 block">Projeto</label>
        <select
          className="w-full h-9 rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px--2 text-sm"
          value={selectedProjectId ?? ''}
          onChange={(e) => setSelectedProjectId(e.target.value || null)}
        >
          <option value="">Selecionar projeto...</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
        <Button
          variant="outline"
          size="sm"
          className="w-full mt-2"
          onClick={async () => {
            const name = prompt('Nome do projeto:')
            if (name) {
              const project = await api.projects.create({ name })
              setSelectedProjectId(project.id)
            }
          }}
        >
          + Novo Projeto
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-[var(--color-muted-foreground)]">Fluxos</span>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={() => fileInputRef.current?.click()}
              disabled={!selectedProjectId}
            >
              <Upload className="h-3.5 w-3.5" />
            </Button>
            <input ref={fileInputRef} type="file" accept=".json,.pdf" className="hidden" onChange={handleUpload} />
          </div>

          {flows.map((flow) => (
            <button
              key={flow.id}
              onClick={() => {
                setSelectedFlowId(flow.id)
                onTabChange('flows')
              }}
              className={`w-full text-left px-3 py-2 rounded-md text-sm mb-1 transition-colors cursor-pointer ${
                selectedFlowId === flow.id
                  ? 'bg-[var(--color-accent)] text-[var(--color-accent-foreground)]'
                  : 'hover:bg-[var(--color-accent)]/50'
              }`}
            >
              <span className="mr-2">{getFlowTypeIcon(flow.flow_type)}</span>
              {flow.name}
              <span className="block text-xs text-[var(--color-muted-foreground)] mt-0.5">
                {flow.node_count} estados · v{flow.version_count}
              </span>
            </button>
          ))}

          {selectedProjectId && flows.length === 0 && (
            <p className="text-xs text-[var(--color-muted-foreground)] px-2 py-4 text-center">
              Nenhum fluxo. Clique em upload para importar.
            </p>
          )}
        </div>
      </ScrollArea>

      <div className="border-t border-[var(--color-border)] p-2">
        {navItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onTabChange(id)}
            disabled={!selectedFlowId && id !== 'flows'}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors cursor-pointer disabled:opacity-40 ${
              activeTab === id
                ? 'bg-[var(--color-primary)] text-[var(--color-primary-foreground)]'
                : 'hover:bg-[var(--color-accent)]'
            }`}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}

        {activeTab === 'search' && (
          <div className="px-3 py-2">
            <Input
              placeholder="Buscar..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        )}
      </div>
    </motion.aside>
  )
}
