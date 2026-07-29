import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Download, FileJson, FileText, Image, FileCode } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/lib/api'

interface DownloadsPanelProps {
  flowId: string
}

const FORMATS = [
  { id: 'pdf', label: 'PDF', icon: FileText, description: 'Documentação completa em PDF' },
  { id: 'png', label: 'PNG', icon: Image, description: 'Imagem do fluxo' },
  { id: 'svg', label: 'SVG', icon: Image, description: 'Gráfico vetorial' },
  { id: 'markdown', label: 'Markdown', icon: FileCode, description: 'Documentação em Markdown' },
  { id: 'html', label: 'HTML', icon: FileCode, description: 'Página HTML interativa' },
  { id: 'json', label: 'JSON Organizado', icon: FileJson, description: 'Grafo estruturado' },
]

export function DownloadsPanel({ flowId }: DownloadsPanelProps) {
  const [exporting, setExporting] = useState<string | null>(null)

  const handleExport = async (format: string) => {
    setExporting(format)
    try {
      const result = await api.export.generate(flowId, format)
      window.open(api.export.downloadUrl(result.id), '_blank')
    } catch (err) {
      console.error(err)
    } finally {
      setExporting(null)
    }
  }

  return (
    <div className="p-6">
      <h2 className="font-semibold text-lg mb-2">Downloads</h2>
      <p className="text-sm text-[var(--color-muted-foreground)] mb-6">
        Exporte o fluxo em diferentes formatos para compartilhar ou arquivar.
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {FORMATS.map(({ id, label, icon: Icon, description }, index) => (
          <motion.div
            key={id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <Icon className="h-5 w-5 text-[var(--color-primary)]" />
                  <CardTitle className="text-base">{label}</CardTitle>
                </div>
                <CardDescription>{description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => handleExport(id)}
                  disabled={exporting === id}
                >
                  <Download className="h-4 w-4 mr-1" />
                  {exporting === id ? 'Exportando...' : 'Baixar'}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
