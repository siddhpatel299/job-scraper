import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { 
      job_type, 
      keywords = '', 
      location = 'United States', 
      time_filter = '7',
      experience_level = 'all',
      sources = ['Indeed'],
      exclude_citizenship_required = false,
      f1_student = false,
      exclude_easy_apply = true
    } = body

    // Create a unique search ID for this request
    const searchId = Date.now().toString()
    
    // Path to your Python scraper
    const pythonScriptPath = path.join(process.cwd(), '..', 'unified_scraper.py')
    const venvPythonPath = path.join(process.cwd(), '..', 'venv', 'bin', 'python')
    
    // Start the Python scraper process
    const pythonProcess = spawn(venvPythonPath, [
      '-c',
      `
import sys
sys.path.append('${path.join(process.cwd(), '..')}')
from job_scraper import CyberSecurityJobScraper, SoftwareEngineeringJobScraper
import json

# Choose scraper based on job type
if '${job_type}' == 'software':
    scraper = SoftwareEngineeringJobScraper()
else:
    scraper = CyberSecurityJobScraper()

# Scrape jobs with all parameters
try:
    jobs = scraper.scrape_all_sources(
        location='${location}',
        sources=${JSON.stringify(sources)},
        time_filter='${time_filter}',
        experience_level='${experience_level}',
        exclude_citizenship_required=${exclude_citizenship_required ? 'True' : 'False'},
        f1_student=${f1_student ? 'True' : 'False'},
        exclude_easy_apply=${exclude_easy_apply ? 'True' : 'False'},
        keywords='${keywords}'
    )
    
    print(json.dumps({
        'success': True,
        'jobs': jobs,
        'search_id': '${searchId}',
        'total_count': len(jobs)
    }))
except Exception as e:
    print(json.dumps({
        'success': False,
        'error': str(e),
        'search_id': '${searchId}'
    }))
      `
    ])

    return new Promise<NextResponse>((resolve) => {
      let output = ''
      let errorOutput = ''

      pythonProcess.stdout.on('data', (data) => {
        output += data.toString()
      })

      pythonProcess.stderr.on('data', (data) => {
        errorOutput += data.toString()
      })

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output.trim())
            resolve(NextResponse.json(result))
          } catch (error) {
            resolve(NextResponse.json({
              success: false,
              error: 'Failed to parse Python output',
              debug: { output, errorOutput }
            }, { status: 500 }))
          }
        } else {
          resolve(NextResponse.json({
            success: false,
            error: 'Python script failed',
            debug: { code, output, errorOutput }
          }, { status: 500 }))
        }
      })
    })

  } catch (error) {
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
