#!/usr/bin/env python3
"""
Test script to verify the web interface fix
"""

import sys
import os
sys.path.append('.')

from job_scraper import CyberSecurityJobScraper

def test_scraper():
    print("🧪 Testing Job Scraper...")
    
    scraper = CyberSecurityJobScraper()
    
    # Test with a small sample
    print("📊 Testing with LinkedIn (1 page)...")
    jobs = scraper.scrape_linkedin_jobs(location="United States", max_pages=1, time_filter="7", experience_level="all")
    
    print(f"✅ Found {len(jobs)} jobs")
    
    if jobs:
        print("\n🔍 Sample job:")
        job = jobs[0]
        print(f"   Title: {job.get('title', 'N/A')}")
        print(f"   Company: {job.get('company', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Source: {job.get('source', 'N/A')}")
        print(f"   URL: {job.get('url', 'N/A')[:50]}...")
        
        # Test F1 filtering
        print("\n🎓 Testing F1 student filtering...")
        f1_jobs = scraper.filter_f1_student_friendly(jobs, f1_student=True)
        print(f"   F1 friendly jobs: {len(f1_jobs)}")
        
        return jobs
    else:
        print("❌ No jobs found")
        return []

if __name__ == "__main__":
    jobs = test_scraper()
    
    if jobs:
        print(f"\n✅ Test successful! Found {len(jobs)} jobs")
        print("🌐 The web interface should now work properly")
    else:
        print("\n❌ Test failed - no jobs found")
        print("🔧 This might be due to rate limiting or network issues")
