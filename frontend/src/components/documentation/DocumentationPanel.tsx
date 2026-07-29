import { useQuery } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { RefreshCw } from 'lucide-react'

interface DocumentationPanelProps {
  flowId: string
}

const SECTIONS = [
  { key: 'summary', label: 'Resumo' },
  { key: 'objective', label: 'Objetivo' },
  { key: 'inputs', label: 'Entradas' },
  { key: 'outputs', label: 'Saídas' },
  { key: 'apis', label: 'APIs' },
  { key: 'variables', label: 'Variáveis' },
  { key: 'flow_description', label: 'Fluxo' },
  { key: 'rules', label: 'Regras' },
  { key: 'exceptions', label: 'Exceções' },
] as const

export function DocumentationPanel({ flowId }: DocumentationPanelProps) {
  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['documentation', flowId],
    queryFn: () => api.documentation.get(flowId),
    enabled: !!flowId,
  })

  if (isLoading) {
    return <div className="p-6 text-[var(--color-muted-foreground)]">Gerando documentação...</div>
  }

  if (!data) return null

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-4 border-b border-[var(--color-border)]">
        <h2 className="font-semibold">Documentação Automática</h2>
        <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isFetching}>
          <RefreshCw className={`h-4 w-4 mr-1 ${isFetching ? 'animate-spin' : ''}`} />
          Regenerar
        </Button>
      </div>
      <Tabs defaultValue="summary" className="flex-1 flex flex-col overflow-hidden">
        <TabsList className="mx-4 mt-2 flex-wrap h-auto">
          {SECTIONS.map(({ key, label }) => (
            <TabsTrigger key={key} value={key} className="text-xs">
              {label}
            </TabsTrigger>
          ))}
        </TabsList>
        <ScrollArea className="flex-1">
          {SECTIONS.map(({ key, label }) => (
            <TabsContent key={key} value={key} className="px-6 pb-6">
              <article className="prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown>{data[key] || `_Sem conteúdo para ${label}_`}</ReactMarkdown>
              </article>
            </TabsContent>
          ))}
        </ScrollArea>
      </Tabs>
    </div>
  )
}
