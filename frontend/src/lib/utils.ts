import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getFlowTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    whatsapp: '📱',
    ura: '☎',
    commercial: '🤖',
    email: '📧',
  }
  return icons[type] ?? '📋'
}

export function getNodeTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    start: 'Início',
    end: 'Fim',
    menu: 'Menu',
    submenu: 'Submenu',
    message: 'Mensagem',
    condition: 'Condição',
    api: 'API',
    variable: 'Variável',
    human_handoff: 'Atendimento Humano',
    error: 'Erro',
    flow: 'Fluxo',
    module: 'Módulo',
    unknown: 'Desconhecido',
  }
  return labels[type] ?? type
}
