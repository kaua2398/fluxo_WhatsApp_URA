import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  theme: 'light' | 'dark'
  sidebarOpen: boolean
  selectedProjectId: string | null
  selectedFlowId: string | null
  selectedModule: string | null
  searchQuery: string
  setTheme: (theme: 'light' | 'dark') => void
  toggleTheme: () => void
  setSidebarOpen: (open: boolean) => void
  setSelectedProjectId: (id: string | null) => void
  setSelectedFlowId: (id: string | null) => void
  setSelectedModule: (module: string | null) => void
  setSearchQuery: (query: string) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      theme: 'light',
      sidebarOpen: true,
      selectedProjectId: null,
      selectedFlowId: null,
      selectedModule: null,
      searchQuery: '',
      setTheme: (theme) => {
        document.documentElement.classList.toggle('dark', theme === 'dark')
        set({ theme })
      },
      toggleTheme: () => {
        const next = get().theme === 'light' ? 'dark' : 'light'
        document.documentElement.classList.toggle('dark', next === 'dark')
        set({ theme: next })
      },
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setSelectedProjectId: (id) => set({ selectedProjectId: id, selectedFlowId: null, selectedModule: null }),
      setSelectedFlowId: (id) => set({ selectedFlowId: id, selectedModule: null }),
      setSelectedModule: (module) => set({ selectedModule: module }),
      setSearchQuery: (query) => set({ searchQuery: query }),
    }),
    {
      name: 'flow-navigator-store',
      partialize: (state) => ({
        theme: state.theme,
        selectedProjectId: state.selectedProjectId,
        selectedFlowId: state.selectedFlowId,
      }),
    }
  )
)
