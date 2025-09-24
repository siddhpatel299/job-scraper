import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { Job, JobSearchFilters, JobSearchResult, JobStats, ScrapingProgress, JobCategory } from '@/types/job'

interface JobStore {
  // State
  jobs: Job[]
  searchResults: JobSearchResult | null
  stats: JobStats | null
  scrapingProgress: ScrapingProgress | null
  isLoading: boolean
  error: string | null
  bookmarkedJobs: string[]
  currentFilters: JobSearchFilters | null
  
  // Actions
  setJobs: (jobs: Job[]) => void
  setSearchResults: (results: JobSearchResult) => void
  setStats: (stats: JobStats) => void
  setScrapingProgress: (progress: ScrapingProgress) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  toggleBookmark: (jobId: string) => void
  clearBookmarks: () => void
  setCurrentFilters: (filters: JobSearchFilters) => void
  clearResults: () => void
  
  // Search actions
  startSearch: (filters: JobSearchFilters) => Promise<void>
  getSearchProgress: (searchId: string) => Promise<void>
  
  // Utility functions
  getFilteredJobs: () => Job[]
  getJobById: (id: string) => Job | undefined
  getBookmarkedJobs: () => Job[]
}

export const useJobStore = create<JobStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        jobs: [],
        searchResults: null,
        stats: null,
        scrapingProgress: null,
        isLoading: false,
        error: null,
        bookmarkedJobs: [],
        currentFilters: null,

        // Actions
        setJobs: (jobs) => set({ jobs }),
        
        setSearchResults: (results) => set({ 
          searchResults: results,
          jobs: results.jobs,
          error: null 
        }),
        
        setStats: (stats) => set({ stats }),
        
        setScrapingProgress: (progress) => set({ scrapingProgress: progress }),
        
        setLoading: (loading) => set({ isLoading: loading }),
        
        setError: (error) => set({ error }),
        
        toggleBookmark: (jobId) => set((state) => ({
          bookmarkedJobs: state.bookmarkedJobs.includes(jobId)
            ? state.bookmarkedJobs.filter(id => id !== jobId)
            : [...state.bookmarkedJobs, jobId]
        })),
        
        clearBookmarks: () => set({ bookmarkedJobs: [] }),
        
        setCurrentFilters: (filters) => set({ currentFilters: filters }),
        
        clearResults: () => set({
          jobs: [],
          searchResults: null,
          stats: null,
          scrapingProgress: null,
          error: null
        }),

        // Search actions
        startSearch: async (filters: JobSearchFilters) => {
          set({ isLoading: true, error: null, currentFilters: filters })
          
          try {
            const response = await fetch('/api/jobs/search', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(filters),
            })

            if (!response.ok) {
              throw new Error(`Search failed: ${response.statusText}`)
            }

            const data = await response.json()
            
            if (data.success) {
              // Start polling for progress
              const searchId = data.search_id
              get().getSearchProgress(searchId)
            } else {
              throw new Error(data.error || 'Search failed')
            }
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Search failed',
              isLoading: false 
            })
          }
        },

        getSearchProgress: async (searchId: string) => {
          try {
            const response = await fetch(`/api/jobs/progress/${searchId}`)
            
            if (!response.ok) {
              throw new Error('Failed to get progress')
            }

            const progress: ScrapingProgress = await response.json()
            set({ scrapingProgress: progress })

            if (progress.status === 'completed') {
              // Fetch final results
              const resultsResponse = await fetch(`/api/jobs/results/${searchId}`)
              if (resultsResponse.ok) {
                const results: JobSearchResult = await resultsResponse.json()
                set({ 
                  searchResults: results,
                  jobs: results.jobs,
                  isLoading: false 
                })
                
                // Fetch stats
                const statsResponse = await fetch(`/api/jobs/stats/${searchId}`)
                if (statsResponse.ok) {
                  const stats: JobStats = await statsResponse.json()
                  set({ stats })
                }
              }
            } else if (progress.status === 'failed') {
              set({ 
                error: progress.error || 'Search failed',
                isLoading: false 
              })
            } else if (progress.status === 'running') {
              // Continue polling
              setTimeout(() => get().getSearchProgress(searchId), 2000)
            }
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Failed to get progress',
              isLoading: false 
            })
          }
        },

        // Utility functions
        getFilteredJobs: () => {
          const { jobs, currentFilters } = get()
          if (!currentFilters) return jobs
          
          return jobs.filter(job => {
            // Apply additional client-side filtering if needed
            if (currentFilters.remote_only && !job.remote_friendly) {
              return false
            }
            
            if (currentFilters.exclude_citizenship_required && job.security_clearance_required) {
              return false
            }
            
            return true
          })
        },

        getJobById: (id: string) => {
          return get().jobs.find(job => job.id === id)
        },

        getBookmarkedJobs: () => {
          const { jobs, bookmarkedJobs } = get()
          return jobs.filter(job => bookmarkedJobs.includes(job.id))
        },
      }),
      {
        name: 'job-store',
        partialize: (state) => ({
          bookmarkedJobs: state.bookmarkedJobs,
          currentFilters: state.currentFilters,
        }),
      }
    ),
    {
      name: 'job-store',
    }
  )
)
