const API_BASE = '/api/v1'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

export const api = {
  projects: {
    list: () => request<import('@/types').Project[]>('/projects'),
    get: (id: string) => request<import('@/types').Project>(`/projects/${id}`),
    create: (data: { name: string; description?: string }) =>
      request<import('@/types').Project>('/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request<void>(`/projects/${id}`, { method: 'DELETE' }),
  },

  flows: {
    list: (projectId: string) =>
      request<import('@/types').Flow[]>(`/flows?project_id=${projectId}`),
    get: (id: string) => request<import('@/types').FlowDetail>(`/flow/${id}`),
    create: (data: { project_id: string; name: string; flow_type: string; description?: string }) =>
      request<import('@/types').Flow>('/flows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request<void>(`/flows/${id}`, { method: 'DELETE' }),
  },

  modules: {
    list: (flowId: string) =>
      request<import('@/types').Module[]>(`/modules?flow_id=${flowId}`),
    nodes: (flowId: string, moduleName: string) =>
      request<import('@/types').FlowNode[]>(
        `/modules/${encodeURIComponent(moduleName)}/nodes?flow_id=${flowId}`
      ),
  },

  upload: (projectId: string, file: File, flowType: string, flowName?: string) => {
    const formData = new FormData()
    formData.append('project_id', projectId)
    formData.append('flow_type', flowType)
    formData.append('file', file)
    if (flowName) formData.append('flow_name', flowName)
    return request<import('@/types').UploadResult>('/upload', {
      method: 'POST',
      body: formData,
    })
  },

  parse: (flowId: string, file: File, flowType?: string) => {
    const formData = new FormData()
    formData.append('flow_id', flowId)
    formData.append('file', file)
    if (flowType) formData.append('flow_type', flowType)
    return request<import('@/types').UploadResult>('/parse', {
      method: 'POST',
      body: formData,
    })
  },

  documentation: {
    get: (flowId: string, regenerate = false) =>
      request<import('@/types').Documentation>(
        `/flow/${flowId}/documentation?regenerate=${regenerate}`
      ),
  },

  versions: {
    list: (flowId: string) =>
      request<import('@/types').Version[]>(`/flow/${flowId}/versions`),
    compare: (flowId: string, versionA: number, versionB: number) =>
      request<import('@/types').ComparisonResult>(
        `/flow/${flowId}/compare?version_a=${versionA}&version_b=${versionB}`
      ),
  },

  search: (flowId: string, query: string) =>
    request<import('@/types').SearchResult[]>(
      `/search?flow_id=${flowId}&q=${encodeURIComponent(query)}`
    ),

  export: {
    generate: (flowId: string, format: string, module?: string) => {
      const params = new URLSearchParams({ flow_id: flowId })
      if (module) params.set('module', module)
      return request<import('@/types').ExportResult>(`/export/${format}?${params}`)
    },
    downloadUrl: (exportId: string) => `${API_BASE}/export/download/${exportId}`,
  },

  nodes: {
    updatePosition: (nodeId: string, x: number, y: number) =>
      request<import('@/types').FlowNode>(
        `/nodes/${nodeId}/position?position_x=${x}&position_y=${y}`,
        { method: 'PATCH' }
      ),
  },
}
