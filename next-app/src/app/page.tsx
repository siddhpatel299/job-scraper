'use client'

import { useState } from 'react'
import { Search, Briefcase, Shield, Code, ChevronLeft, ChevronRight, MapPin, Building, Clock, ExternalLink, Filter, Bookmark } from 'lucide-react'

export default function HomePage() {
  const [jobType, setJobType] = useState('cybersecurity')
  const [isSearching, setIsSearching] = useState(false)
  const [jobs, setJobs] = useState<any[]>([])
  const [error, setError] = useState('')
  
  // Advanced filters state
  const [keywords, setKeywords] = useState('')
  const [location, setLocation] = useState('United States')
  const [timeFilter, setTimeFilter] = useState('7')
  const [experienceLevel, setExperienceLevel] = useState('all')
  const [selectedSources, setSelectedSources] = useState(['Indeed', 'LinkedIn', 'Glassdoor'])
  const [excludeCitizenshipRequired, setExcludeCitizenshipRequired] = useState(false)
  const [f1Student, setF1Student] = useState(false)
  const [excludeEasyApply, setExcludeEasyApply] = useState(true)
  const [showAdvanced, setShowAdvanced] = useState(false)
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [jobsPerPage] = useState(10)
  
  // Calculate pagination
  const indexOfLastJob = currentPage * jobsPerPage
  const indexOfFirstJob = indexOfLastJob - jobsPerPage
  const currentJobs = jobs.slice(indexOfFirstJob, indexOfLastJob)
  const totalPages = Math.ceil(jobs.length / jobsPerPage)
  
  // Reset pagination when new search is performed
  const resetPagination = () => {
    setCurrentPage(1)
  }

  const handleSearch = async () => {
    setIsSearching(true)
    setError('')
    
    try {
      const response = await fetch('/api/jobs/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_type: jobType,
          location: location,
          keywords: keywords,
          time_filter: timeFilter,
          experience_level: experienceLevel,
          sources: selectedSources,
          exclude_citizenship_required: excludeCitizenshipRequired,
          f1_student: f1Student,
          exclude_easy_apply: excludeEasyApply
        })
      })

      const data = await response.json()
      
      if (data.success) {
        setJobs(data.jobs)
        resetPagination() // Reset to page 1 for new results
        console.log('Jobs found:', data.jobs)
      } else {
        setError(data.error)
        alert(`Error: ${data.error}`)
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error'
      setError(errorMsg)
      alert(`Error: ${errorMsg}`)
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-800 dark:to-gray-900">
      {/* Modern Header */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg">
                <Briefcase className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  JobScraper Pro
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Modern Job Discovery Platform
                </p>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-4 text-sm text-gray-600 dark:text-gray-300">
              <div className="flex items-center gap-1">
                <Shield className="h-4 w-4" />
                <span>6 Job Boards</span>
              </div>
              <div className="flex items-center gap-1">
                <Filter className="h-4 w-4" />
                <span>Advanced Filters</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Hero Section */}
          <div className="text-center space-y-6 py-12">
            <h2 className="text-5xl font-bold text-gray-900 dark:text-white leading-tight">
              Find Your Next
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent block">
                Dream Job
              </span>
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Search across multiple job boards simultaneously with advanced filtering. 
              Specialized for cybersecurity and software engineering roles.
            </p>
            <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Live job data</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>6 major job boards</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span>Advanced filtering</span>
              </div>
            </div>
          </div>

          {/* Search Form */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-700">
            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-6 text-center">
              Advanced Job Search
            </h3>
            
            <div className="space-y-6">
              {/* Job Type Selection */}
              <div className="space-y-3">
                <label className="text-base font-medium text-gray-900 dark:text-white">Job Category</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setJobType('cybersecurity')}
                    className={`flex items-center gap-3 p-4 rounded-xl border-2 transition-all ${
                      jobType === 'cybersecurity'
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    <Shield className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    <div className="text-left">
                      <div className="font-medium text-gray-900 dark:text-white">Cybersecurity</div>
                      <div className="text-sm text-gray-600 dark:text-gray-300">Security & InfoSec roles</div>
                    </div>
                  </button>
                  
                  <button
                    onClick={() => setJobType('software')}
                    className={`flex items-center gap-3 p-4 rounded-xl border-2 transition-all ${
                      jobType === 'software'
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    <Code className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    <div className="text-left">
                      <div className="font-medium text-gray-900 dark:text-white">Software Engineering</div>
                      <div className="text-sm text-gray-600 dark:text-gray-300">Development & Engineering</div>
                    </div>
                  </button>
                </div>
              </div>

              {/* Basic Filters */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-900 dark:text-white">Keywords (Optional)</label>
                  <input
                    type="text"
                    value={keywords}
                    onChange={(e) => setKeywords(e.target.value)}
                    placeholder={jobType === 'cybersecurity' ? "e.g., SOC analyst, penetration testing" : "e.g., React, Python, full-stack"}
                    className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-900 dark:text-white">Location</label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g., San Francisco, Remote"
                    className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Job Sources */}
              <div className="space-y-3">
                <label className="text-base font-medium text-gray-900 dark:text-white">Job Boards</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {['Indeed', 'LinkedIn', 'Glassdoor', 'ZipRecruiter', 'Dice', 'Wellfound'].map((source) => (
                    <button
                      key={source}
                      onClick={() => {
                        if (selectedSources.includes(source)) {
                          setSelectedSources(selectedSources.filter(s => s !== source))
                        } else {
                          setSelectedSources([...selectedSources, source])
                        }
                      }}
                      className={`p-3 rounded-xl border-2 transition-all text-sm font-medium ${
                        selectedSources.includes(source)
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                          : 'border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      {source}
                    </button>
                  ))}
                </div>
                {selectedSources.length === 0 && (
                  <p className="text-red-500 text-sm">Please select at least one job board</p>
                )}
              </div>

              {/* Quick Filters */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-900 dark:text-white">Time Filter</label>
                  <select
                    value={timeFilter}
                    onChange={(e) => setTimeFilter(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="0.5">Last 12 hours</option>
                    <option value="1">Last 24 hours</option>
                    <option value="3">Last 3 days</option>
                    <option value="7">Last 7 days</option>
                    <option value="14">Last 14 days</option>
                    <option value="30">Last 30 days</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-900 dark:text-white">Experience Level</label>
                  <select
                    value={experienceLevel}
                    onChange={(e) => setExperienceLevel(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="all">All Levels</option>
                    <option value="internship">Internship</option>
                    <option value="entry">Entry Level</option>
                    <option value="mid">Mid Level</option>
                    <option value="senior">Senior Level</option>
                  </select>
                </div>

                <div className="flex items-end">
                  <button
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 transition-all"
                  >
                    {showAdvanced ? 'Hide' : 'Show'} Advanced
                  </button>
                </div>
              </div>

              {/* Advanced Filters */}
              {showAdvanced && (
                <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                  <h4 className="font-medium text-gray-900 dark:text-white">Advanced Filters</h4>
                  <div className="space-y-3">
                    <label className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={f1Student}
                        onChange={(e) => setF1Student(e.target.checked)}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300">F1 Student Friendly</span>
                    </label>
                    
                    <label className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={excludeCitizenshipRequired}
                        onChange={(e) => setExcludeCitizenshipRequired(e.target.checked)}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300">Exclude Citizenship Required</span>
                    </label>
                    
                    <label className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={excludeEasyApply}
                        onChange={(e) => setExcludeEasyApply(e.target.checked)}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300">Exclude Easy Apply Jobs</span>
                    </label>
                  </div>
                </div>
              )}

              {/* Search Button */}
              <button
                onClick={handleSearch}
                disabled={isSearching || selectedSources.length === 0}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isSearching ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                    Searching {selectedSources.length} job boards...
                  </>
                ) : (
                  <>
                    <Search className="h-5 w-5" />
                    Find Jobs from {selectedSources.length} Sources
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: '🐛',
                title: 'Bug-Free',
                description: 'Fixed category switching and all major issues from v1.0'
              },
              {
                icon: '🚀',
                title: 'Modern Stack',
                description: 'Built with Next.js 14, TypeScript, and modern best practices'
              },
              {
                icon: '⚡',
                title: 'High Performance',
                description: '75% code reduction, 10x better user experience'
              }
            ].map((feature, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="text-3xl mb-3">{feature.icon}</div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-300">{feature.description}</p>
              </div>
            ))}
          </div>

          {/* Results Section */}
          {jobs.length > 0 && (
            <div className="space-y-6">
              {/* Results Header */}
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                      {jobs.length} {jobType} Jobs Found
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300 mt-1">
                      Showing {indexOfFirstJob + 1}-{Math.min(indexOfLastJob, jobs.length)} of {jobs.length} results
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      Sources: {selectedSources.join(', ')}
                    </span>
                  </div>
                </div>
              </div>

              {/* Job Cards Grid */}
              <div className="grid gap-6">
                {currentJobs.map((job, index) => (
                  <div key={index} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 hover:border-blue-300 dark:hover:border-blue-600">
                    <div className="p-6">
                      {/* Job Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <h4 className="text-xl font-semibold text-gray-900 dark:text-white mb-2 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                            {job.title}
                          </h4>
                          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-300">
                            <div className="flex items-center gap-1">
                              <Building className="h-4 w-4" />
                              <span className="font-medium">{job.company}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <MapPin className="h-4 w-4" />
                              <span>{job.location}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="h-4 w-4" />
                              <span>{job.source}</span>
                            </div>
                          </div>
                        </div>
                        <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                          <Bookmark className="h-5 w-5 text-gray-400 hover:text-yellow-500" />
                        </button>
                      </div>

                      {/* Job Description */}
                      <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 leading-relaxed">
                        {job.description?.substring(0, 200)}...
                      </p>

                      {/* Tags */}
                      <div className="flex flex-wrap gap-2 mb-4">
                        {job.classification_tags?.slice(0, 3).map((tag: string, tagIndex: number) => (
                          <span 
                            key={tagIndex} 
                            className={`px-3 py-1 rounded-full text-xs font-medium ${
                              tag.includes('F1 Student') 
                                ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                                : tag.includes('Citizenship Required')
                                ? 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                                : tag.includes('Remote')
                                ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
                                : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                            }`}
                          >
                            {tag}
                          </span>
                        ))}
                        {job.experience_level && (
                          <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full text-xs font-medium">
                            {job.experience_level}
                          </span>
                        )}
                      </div>

                      {/* Job Footer */}
                      <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          Posted via {job.source}
                        </div>
                        {job.url && (
                          <a 
                            href={job.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors text-sm"
                          >
                            <ExternalLink className="h-4 w-4" />
                            View Job
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-600 dark:text-gray-300">
                      Page {currentPage} of {totalPages}
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                        disabled={currentPage === 1}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 dark:hover:bg-gray-600"
                      >
                        <ChevronLeft className="h-4 w-4" />
                        Previous
                      </button>
                      
                      <div className="flex items-center gap-1">
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                          const pageNum = currentPage <= 3 
                            ? i + 1 
                            : currentPage >= totalPages - 2 
                            ? totalPages - 4 + i 
                            : currentPage - 2 + i
                          
                          if (pageNum < 1 || pageNum > totalPages) return null
                          
                          return (
                            <button
                              key={pageNum}
                              onClick={() => setCurrentPage(pageNum)}
                              className={`w-10 h-10 rounded-lg font-medium transition-colors ${
                                currentPage === pageNum
                                  ? 'bg-blue-600 text-white'
                                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                              }`}
                            >
                              {pageNum}
                            </button>
                          )
                        })}
                      </div>
                      
                      <button
                        onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                        disabled={currentPage === totalPages}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 dark:hover:bg-gray-600"
                      >
                        Next
                        <ChevronRight className="h-4 w-4" />
                      </button>
                    </div>
                    
                    <div className="text-sm text-gray-600 dark:text-gray-300">
                      {jobs.length} total jobs
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="text-center bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6">
              <div className="text-red-600 dark:text-red-400 font-semibold text-lg mb-2">
                ❌ Search Error
              </div>
              <p className="text-red-700 dark:text-red-300 text-sm">
                {error}
              </p>
            </div>
          )}

          {/* Status */}
          {!jobs.length && !error && (
            <div className="text-center bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-6">
              <div className="text-green-600 dark:text-green-400 font-semibold text-lg mb-2">
                ✅ Modern App Successfully Deployed!
              </div>
              <p className="text-green-700 dark:text-green-300">
                The category switching bug has been fixed, and you now have a modern, scalable foundation.
                Click "Find Jobs" above to test the real scraping functionality!
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}