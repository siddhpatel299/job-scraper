'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { 
  Search, 
  MapPin, 
  Clock, 
  User, 
  Settings2, 
  Loader2,
  Shield,
  Code,
  Filter,
  X
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { useJobStore } from '@/store/job-store'
import { JobCategory, JobSource, ExperienceLevel, TimeFilter } from '@/types/job'

const searchSchema = z.object({
  category: z.enum(['cybersecurity', 'software-engineering'] as const),
  keywords: z.string().optional(),
  location: z.string().min(1, 'Location is required'),
  sources: z.array(z.enum(['indeed', 'linkedin', 'glassdoor', 'ziprecruiter', 'dice', 'wellfound', 'google-dorks'] as const)).min(1, 'Select at least one source'),
  experience_level: z.enum(['all', 'entry', 'mid', 'senior', 'lead', 'executive'] as const),
  time_filter: z.enum(['12h', '24h', '3d', '7d', '14d', '30d'] as const),
  max_pages: z.number().min(1).max(10),
  exclude_citizenship_required: z.boolean(),
  f1_student_friendly: z.boolean(),
  remote_only: z.boolean(),
  exclude_easy_apply: z.boolean(),
  use_google_dorks: z.boolean(),
  serp_api_key: z.string().optional(),
})

type SearchForm = z.infer<typeof searchSchema>

interface JobSearchFormProps {
  onSearchComplete?: () => void
}

export function JobSearchForm({ onSearchComplete }: JobSearchFormProps) {
  const { startSearch, isLoading, error, clearResults } = useJobStore()
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [selectedSources, setSelectedSources] = useState<JobSource[]>(['indeed', 'linkedin', 'glassdoor'])

  const form = useForm<SearchForm>({
    resolver: zodResolver(searchSchema),
    defaultValues: {
      category: 'cybersecurity',
      keywords: '',
      location: 'United States',
      sources: ['indeed', 'linkedin', 'glassdoor'],
      experience_level: 'all',
      time_filter: '7d',
      max_pages: 3,
      exclude_citizenship_required: false,
      f1_student_friendly: false,
      remote_only: false,
      exclude_easy_apply: true,
      use_google_dorks: false,
      serp_api_key: '',
    },
  })

  const watchCategory = form.watch('category')
  const watchUseGoogleDorks = form.watch('use_google_dorks')

  // Clear results when category changes
  useEffect(() => {
    clearResults()
  }, [watchCategory, clearResults])

  const onSubmit = async (data: SearchForm) => {
    try {
      await startSearch({
        ...data,
        sources: selectedSources,
      })
      onSearchComplete?.()
    } catch (error) {
      console.error('Search failed:', error)
    }
  }

  const toggleSource = (source: JobSource) => {
    setSelectedSources(prev => 
      prev.includes(source) 
        ? prev.filter(s => s !== source)
        : [...prev, source]
    )
    form.setValue('sources', selectedSources.includes(source) 
      ? selectedSources.filter(s => s !== source)
      : [...selectedSources, source]
    )
  }

  const sourceConfig = [
    { id: 'indeed' as const, name: 'Indeed', description: 'Largest job board' },
    { id: 'linkedin' as const, name: 'LinkedIn', description: 'Professional network' },
    { id: 'glassdoor' as const, name: 'Glassdoor', description: 'Company reviews & jobs' },
    { id: 'ziprecruiter' as const, name: 'ZipRecruiter', description: 'Quick applications' },
    { id: 'dice' as const, name: 'Dice', description: 'Tech-focused jobs' },
    { id: 'wellfound' as const, name: 'Wellfound', description: 'Startup jobs' },
    { id: 'google-dorks' as const, name: 'Google Dorks', description: 'ATS platforms' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {/* Job Category */}
        <div className="space-y-3">
          <Label className="text-base font-medium">Job Category</Label>
          <div className="grid grid-cols-2 gap-3">
            <div className="relative">
              <input
                type="radio"
                id="cybersecurity"
                value="cybersecurity"
                {...form.register('category')}
                className="peer sr-only"
              />
              <label
                htmlFor="cybersecurity"
                className="flex items-center gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all peer-checked:border-primary peer-checked:bg-primary/5 hover:bg-muted/50"
              >
                <Shield className="h-5 w-5 text-primary" />
                <div>
                  <div className="font-medium">Cybersecurity</div>
                  <div className="text-sm text-muted-foreground">Security & InfoSec roles</div>
                </div>
              </label>
            </div>
            
            <div className="relative">
              <input
                type="radio"
                id="software-engineering"
                value="software-engineering"
                {...form.register('category')}
                className="peer sr-only"
              />
              <label
                htmlFor="software-engineering"
                className="flex items-center gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all peer-checked:border-primary peer-checked:bg-primary/5 hover:bg-muted/50"
              >
                <Code className="h-5 w-5 text-primary" />
                <div>
                  <div className="font-medium">Software Engineering</div>
                  <div className="text-sm text-muted-foreground">Development & Engineering</div>
                </div>
              </label>
            </div>
          </div>
        </div>

        {/* Basic Filters */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="keywords">Keywords (Optional)</Label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                id="keywords"
                placeholder={watchCategory === 'cybersecurity' ? "e.g., SOC analyst, penetration testing" : "e.g., React, Python, full-stack"}
                className="pl-10"
                {...form.register('keywords')}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="location">Location</Label>
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                id="location"
                placeholder="e.g., San Francisco, Remote"
                className="pl-10"
                {...form.register('location')}
              />
            </div>
          </div>
        </div>

        {/* Job Sources */}
        <div className="space-y-3">
          <Label className="text-base font-medium">Job Sources</Label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {sourceConfig.map((source) => (
              <div key={source.id}>
                <Button
                  type="button"
                  variant={selectedSources.includes(source.id) ? "default" : "outline"}
                  size="sm"
                  className="w-full justify-start text-left h-auto p-3"
                  onClick={() => toggleSource(source.id)}
                >
                  <div>
                    <div className="font-medium text-sm">{source.name}</div>
                    <div className="text-xs opacity-70">{source.description}</div>
                  </div>
                </Button>
              </div>
            ))}
          </div>
          {selectedSources.length === 0 && (
            <p className="text-sm text-destructive">Please select at least one job source</p>
          )}
        </div>

        {/* Quick Filters */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-2">
            <Label>⚡ TIME FILTER UPDATED ⚡</Label>
            <Select value={form.watch('time_filter')} onValueChange={(value) => form.setValue('time_filter', value as TimeFilter)}>
              <SelectTrigger>
                <Clock className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {/* 12h option added */}
                <SelectItem value="12h">🔥 Last 12 hours 🔥</SelectItem>
                <SelectItem value="24h">Last 24 hours</SelectItem>
                <SelectItem value="3d">Last 3 days</SelectItem>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="14d">Last 14 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Experience Level</Label>
            <Select value={form.watch('experience_level')} onValueChange={(value) => form.setValue('experience_level', value as ExperienceLevel | 'all')}>
              <SelectTrigger>
                <User className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Levels</SelectItem>
                <SelectItem value="entry">Entry Level</SelectItem>
                <SelectItem value="mid">Mid Level</SelectItem>
                <SelectItem value="senior">Senior Level</SelectItem>
                <SelectItem value="lead">Lead/Staff</SelectItem>
                <SelectItem value="executive">Executive</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Pages per Source</Label>
            <Select value={form.watch('max_pages').toString()} onValueChange={(value) => form.setValue('max_pages', parseInt(value))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">1 page</SelectItem>
                <SelectItem value="2">2 pages</SelectItem>
                <SelectItem value="3">3 pages</SelectItem>
                <SelectItem value="5">5 pages</SelectItem>
                <SelectItem value="10">10 pages</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-end">
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full"
            >
              <Settings2 className="h-4 w-4 mr-2" />
              {showAdvanced ? 'Hide' : 'Show'} Advanced
            </Button>
          </div>
        </div>

        {/* Advanced Filters */}
        <Collapsible open={showAdvanced} onOpenChange={setShowAdvanced}>
          <CollapsibleContent className="space-y-4">
            <Separator />
            
            <div className="space-y-4">
              <h3 className="font-medium flex items-center gap-2">
                <Filter className="h-4 w-4" />
                Advanced Filters
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="f1_student_friendly"
                      checked={form.watch('f1_student_friendly')}
                      onCheckedChange={(checked) => form.setValue('f1_student_friendly', !!checked)}
                    />
                    <Label htmlFor="f1_student_friendly" className="text-sm">
                      F1 Student Friendly
                    </Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="exclude_citizenship_required"
                      checked={form.watch('exclude_citizenship_required')}
                      onCheckedChange={(checked) => form.setValue('exclude_citizenship_required', !!checked)}
                    />
                    <Label htmlFor="exclude_citizenship_required" className="text-sm">
                      Exclude Citizenship Required
                    </Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="remote_only"
                      checked={form.watch('remote_only')}
                      onCheckedChange={(checked) => form.setValue('remote_only', !!checked)}
                    />
                    <Label htmlFor="remote_only" className="text-sm">
                      Remote Only
                    </Label>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="exclude_easy_apply"
                      checked={form.watch('exclude_easy_apply')}
                      onCheckedChange={(checked) => form.setValue('exclude_easy_apply', !!checked)}
                    />
                    <Label htmlFor="exclude_easy_apply" className="text-sm">
                      Exclude Easy Apply Jobs
                    </Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="use_google_dorks"
                      checked={form.watch('use_google_dorks')}
                      onCheckedChange={(checked) => form.setValue('use_google_dorks', !!checked)}
                    />
                    <Label htmlFor="use_google_dorks" className="text-sm">
                      Include Google Dorks (ATS)
                    </Label>
                  </div>
                  
                  {watchUseGoogleDorks && (
                    <div className="space-y-2">
                      <Label htmlFor="serp_api_key" className="text-sm text-muted-foreground">
                        SERP API Key (Optional)
                      </Label>
                      <Input
                        id="serp_api_key"
                        type="password"
                        placeholder="Enter SERP API key"
                        {...form.register('serp_api_key')}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          </CollapsibleContent>
        </Collapsible>

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 rounded-lg bg-destructive/10 border border-destructive/20"
          >
            <div className="flex items-center gap-2 text-destructive">
              <X className="h-4 w-4" />
              <span className="text-sm font-medium">Search Failed</span>
            </div>
            <p className="text-sm text-destructive/80 mt-1">{error}</p>
          </motion.div>
        )}

        {/* Submit Button */}
        <Button
          type="submit"
          size="lg"
          disabled={isLoading || selectedSources.length === 0}
          className="w-full"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Searching Jobs...
            </>
          ) : (
            <>
              <Search className="h-4 w-4 mr-2" />
              Find Jobs
            </>
          )}
        </Button>
      </form>
    </motion.div>
  )
}
