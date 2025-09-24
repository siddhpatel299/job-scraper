'use client'

import { motion } from 'framer-motion'
import { useJobStore } from '@/store/job-store'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ExternalLink, MapPin, Building, Calendar, Bookmark } from 'lucide-react'
import { formatRelativeTime, truncate } from '@/lib/utils'

export function JobResults() {
  const { jobs, isLoading, searchResults, toggleBookmark, bookmarkedJobs } = useJobStore()

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(6)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-6 bg-muted rounded w-3/4"></div>
              <div className="h-4 bg-muted rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="h-4 bg-muted rounded"></div>
                <div className="h-4 bg-muted rounded w-5/6"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (!jobs.length) {
    return (
      <Card className="text-center py-12">
        <CardContent>
          <div className="space-y-4">
            <div className="text-muted-foreground text-lg">No jobs found</div>
            <p className="text-muted-foreground">
              Try adjusting your search criteria or filters
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Job Results</h2>
        <Badge variant="secondary" className="text-sm">
          {jobs.length} jobs found
        </Badge>
      </div>

      <div className="space-y-4">
        {jobs.map((job, index) => (
          <motion.div
            key={job.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <CardTitle className="text-xl">{job.title}</CardTitle>
                    <div className="flex items-center gap-4 text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Building className="h-4 w-4" />
                        <span>{job.company}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="h-4 w-4" />
                        <span>{job.location}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>{formatRelativeTime(job.posted_date)}</span>
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => toggleBookmark(job.id)}
                    className={bookmarkedJobs.includes(job.id) ? 'text-yellow-500' : ''}
                  >
                    <Bookmark className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-muted-foreground">
                    {truncate(job.description, 200)}
                  </p>
                  
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="outline">{job.source}</Badge>
                    {job.experience_level && (
                      <Badge variant="outline">{job.experience_level}</Badge>
                    )}
                    {job.remote_friendly && (
                      <Badge variant="outline" className="bg-green-50 text-green-700">
                        Remote Friendly
                      </Badge>
                    )}
                    {job.visa_sponsorship && (
                      <Badge variant="outline" className="bg-blue-50 text-blue-700">
                        Visa Sponsorship
                      </Badge>
                    )}
                    {job.classification_tags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  
                  <div className="flex items-center justify-between pt-2">
                    <div className="text-sm text-muted-foreground">
                      Source: {job.source}
                    </div>
                    <Button asChild>
                      <a href={job.url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4 mr-2" />
                        View Job
                      </a>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}
