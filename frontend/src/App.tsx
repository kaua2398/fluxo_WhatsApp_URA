import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Sidebar } from './components/sidebar/Sidebar'
import { FlowCanvas } from './components/flow/FlowCanvas'
import { MindMapView } from './components/modules/MindMapView'
import { DetailPanel } from './components/layout/DetailPanel'
import { DocumentationPanel } from './components/documentation/DocumentationPanel'
import { ComparisonPanel } from './components/comparison/ComparisonPanel'
import { DownloadsPanel } from './components/documentation/DownloadsPanel'
import { useAppStore } from './stores/appStore'
import { api } from './lib/api'
import type { FlowNode } from './types'

export default function App() {
  const [activeTab, setActiveTab] = useState('flows')
  const [selectedNode, setSelectedNode] = useState<FlowNode | null>(null)

  const selectedProjectId = useAppStore((state) => state.selectedProjectId)
  const selectedFlowId = useAppStore((state) => state.selectedFlowId)
  const selectedModule = useAppStore((state) => state.selectedModule)
  const setSelectedModule = useAppStore((state) => state.setSelectedModule)

  const { data: flowDetail } = useQuery({
    queryKey: ['flowDetail', selectedFlowId],
    queryFn: () => (selectedFlowId ? api.flows.get(selectedFlowId) : Promise.resolve(null)),
    enabled: !!selectedFlowId,
  })

  const { data: modules = [] } = useQuery({
    queryKey: ['modules', selectedFlowId],
    queryFn: () => (selectedFlowId ? api.modules.list(selectedFlowId) : Promise.resolve([])),
    enabled: !!selectedFlowId,
  })

  const flowId = selectedFlowId ?? ''
  const nodes = flowDetail?.nodes ?? []
  const edges = flowDetail?.edges ?? []
  const flowName = flowDetail?.name ?? ''
  const flowType = flowDetail?.flow_type ?? ''
  const projectSelected = Boolean(selectedProjectId)

  useEffect(() => {
    if (!selectedProjectId) {
      setActiveTab('flows')
    }
  }, [selectedProjectId])

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-foreground">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="flex-1 flex flex-col relative overflow-hidden">
        {!projectSelected ? (
          <div className="flex-1 flex items-center justify-center text-muted-foreground p-8 text-center">
            <div>
              <h2 className="text-xl font-semibold mb-2">Nenhum projeto selecionado</h2>
              <p>Selecione um projeto na barra lateral para começar.</p>
            </div>
          </div>
        ) : !selectedFlowId ? (
          <div className="flex-1 flex items-center justify-center text-muted-foreground p-8 text-center">
            <div>
              <h2 className="text-xl font-semibold mb-2">Nenhum fluxo selecionado</h2>
              <p>Escolha um fluxo na barra lateral para visualizar ou exportar.</p>
            </div>
          </div>
        ) : (
          <>
            {(activeTab === 'flows' || activeTab === 'search') && (
              <FlowCanvas
                nodes={nodes}
                edges={edges}
                flowId={flowId}
                moduleFilter={selectedModule}
                onNodeClick={setSelectedNode}
              />
            )}
            {activeTab === 'mindmap' && (
              <MindMapView
                flowName={flowName}
                flowType={flowType}
                modules={modules}
                onModuleClick={(module) => setSelectedModule(module.name)}
              />
            )}
            {activeTab === 'docs' && <DocumentationPanel flowId={flowId} />}
            {activeTab === 'downloads' && <DownloadsPanel flowId={flowId} />}
            {activeTab === 'versions' && <ComparisonPanel flowId={flowId} />}
          </>
        )}
      </main>

      {selectedNode && <DetailPanel node={selectedNode} onClose={() => setSelectedNode(null)} />}
    </div>
  )
}
