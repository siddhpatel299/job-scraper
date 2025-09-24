'use client'

import { motion } from 'framer-motion'
import { useJobStore } from '@/store/job-store'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, Users, MapPin, Building, Clock, Shield } from 'lucide-react'

export function StatsOverview() {
  const { jobs, stats, searchResults } = useJobStore()

  if (!jobs.length) return null

  // Calculate basic stats from jobs data
  const totalJobs = jobs.length
  const sources = Array.from(new Set(jobs.map(job => job.source)))
  const locations = Array.from(new Set(jobs.map(job => job.location)))
  const companies = Array.from(new Set(jobs.map(job => job.company)))
  const remoteJobs = jobs.filter(job => job.remote_friendly).length
  const visaSponsorshipJobs = jobs.filter(job => job.visa_sponsorship).length

  const statCards = [
    {
      title: "Total Jobs",
      value: totalJobs,
      icon: TrendingUp,
      description: "jobs found",
      color: "text-blue-600"
    },
    {
      title: "Job Sources",
      value: sources.length,
      icon: Building,
      description: "sources scraped",
      color: "text-green-600"
    },
    {
      title: "Locations",
      value: locations.length,
      icon: MapPin,
      description: "unique locations",
      color: "text-purple-600"
    },
    {
      title: "Companies",
      value: companies.length,
      icon: Users,
      description: "hiring companies",
      color: "text-orange-600"
    },
    {
      title: "Remote Jobs",
      value: remoteJobs,
      icon: Clock,
      description: "remote friendly",
      color: "text-emerald-600"
    },
    {
      title: "Visa Sponsorship",
      value: visaSponsorshipJobs,
      icon: Shield,
      description: "sponsor visas",
      color: "text-indigo-600"
    }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Search Overview</h2>
        {searchResults && (
          <Badge variant="outline" className="text-sm">
            Search completed in {Math.round(searchResults.scraping_duration / 1000)}s
          </Badge>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="text-center">
              <CardHeader className="pb-2">
                <div className={`mx-auto w-8 h-8 rounded-lg bg-muted flex items-center justify-center ${stat.color}`}>
                  <stat.icon className="h-4 w-4" />
                </div>
                <CardTitle className="text-2xl font-bold">{stat.value}</CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="text-sm font-medium">{stat.title}</div>
                <div className="text-xs text-muted-foreground">{stat.description}</div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Top Sources */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Top Job Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {sources.slice(0, 5).map((source) => {
                const count = jobs.filter(job => job.source === source).length
                const percentage = Math.round((count / totalJobs) * 100)
                return (
                  <div key={source} className="flex items-center justify-between">
                    <span className="text-sm font-medium">{source}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-primary transition-all duration-500"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <span className="text-sm text-muted-foreground w-8 text-right">
                        {count}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Top Locations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {locations.slice(0, 5).map((location) => {
                const count = jobs.filter(job => job.location === location).length
                const percentage = Math.round((count / totalJobs) * 100)
                return (
                  <div key={location} className="flex items-center justify-between">
                    <span className="text-sm font-medium truncate max-w-[120px]">
                      {location}
                    </span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-secondary transition-all duration-500"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <span className="text-sm text-muted-foreground w-8 text-right">
                        {count}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  )
}
