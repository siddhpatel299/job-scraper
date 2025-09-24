#!/usr/bin/env python3
"""
Command-line interface for the Cybersecurity Job Scraper
"""

import argparse
import sys
import os
import socket
from job_scraper import CyberSecurityJobScraper

def find_available_port(start_port=5000, max_port=5100):
    """Find an available port starting from start_port"""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available port found in range {start_port}-{max_port}")

def main():
    parser = argparse.ArgumentParser(description='Cybersecurity Job Scraper CLI')
    parser.add_argument('--location', '-l', default='United States', 
                       help='Location to search for jobs (default: United States)')
    parser.add_argument('--sources', '-s', nargs='+', 
                       choices=['indeed', 'linkedin', 'glassdoor', 'ziprecruiter', 'dice', 'wellfound', 'google-dorks', 'all'],
                       default=['all'], help='Job sources to scrape')
    parser.add_argument('--output', '-o', 
                       choices=['csv', 'json', 'pdf', 'all'], default='all',
                       help='Output format')
    parser.add_argument('--pages', '-p', type=int, default=3,
                       help='Number of pages to scrape per source')
    parser.add_argument('--time-filter', '-t', 
                       choices=['24h', '3d', '7d', '14d', '30d'], default='7d',
                       help='Time filter for job postings (default: 7d)')
    parser.add_argument('--experience', '-e',
                       choices=['all', 'entry', 'internship', 'mid', 'senior'], default='all',
                       help='Experience level filter (default: all)')
    parser.add_argument('--citizenship', '-c', action='store_true',
                       help='Filter for jobs requiring US citizenship')
    parser.add_argument('--f1-student', '-f', action='store_true',
                       help='Filter for F1 student friendly jobs (excludes US citizenship/security clearance requirements)')
    parser.add_argument('--no-dedup', action='store_true',
                       help='Skip duplicate removal')
    parser.add_argument('--web', '-w', action='store_true',
                       help='Start web interface after scraping')
    
    args = parser.parse_args()
    
    # Convert source names to proper case
    source_mapping = {
        'indeed': 'Indeed',
        'linkedin': 'LinkedIn', 
        'glassdoor': 'Glassdoor',
        'ziprecruiter': 'ZipRecruiter',
        'dice': 'Dice',
        'wellfound': 'Wellfound',
        'google-dorks': 'Google Dorks'
    }
    
    if 'all' in args.sources:
        sources = ['Indeed', 'LinkedIn', 'Glassdoor', 'ZipRecruiter', 'Dice', 'Wellfound', 'Google Dorks']
    else:
        sources = [source_mapping[s] for s in args.sources]
    
    print("🛡️ Cybersecurity Job Scraper - Enhanced")
    print("=" * 50)
    print(f"Location: {args.location}")
    print(f"Sources: {', '.join(sources)}")
    print(f"Pages per source: {args.pages}")
    print(f"Time filter: {args.time_filter}")
    print(f"Experience level: {args.experience}")
    print(f"Output format: {args.output}")
    print()
    
    scraper = CyberSecurityJobScraper()
    
    # Use the enhanced scraping method
    all_jobs = scraper.scrape_all_sources(
        location=args.location,
        time_filter=args.time_filter,
        experience_level=args.experience,
        sources=sources,
        exclude_citizenship_required=args.citizenship,
        f1_student=getattr(args, 'f1_student', False)
    )
    
    # Remove duplicates unless explicitly disabled
    if not args.no_dedup:
        all_jobs = scraper.remove_duplicates(all_jobs)
    
    print(f"🎯 Total jobs found: {len(all_jobs)}")
    
    if all_jobs:
        # Show summary by source
        source_counts = {}
        for job in all_jobs:
            source = job['source']
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print("\n📈 Jobs by source:")
        for source, count in source_counts.items():
            print(f"   {source}: {count} jobs")
        
        # Show sponsored jobs count
        sponsored_count = sum(1 for job in all_jobs if job.get('sponsored', False))
        if sponsored_count > 0:
            print(f"   💰 Sponsored jobs: {sponsored_count}")
        
        # Show experience level breakdown
        exp_counts = {}
        for job in all_jobs:
            exp_level = job.get('experience_level', 'unknown')
            exp_counts[exp_level] = exp_counts.get(exp_level, 0) + 1
        
        if len(exp_counts) > 1:
            print("\n🎯 Jobs by experience level:")
            for exp_level, count in exp_counts.items():
                if exp_level != 'unknown':
                    print(f"   {exp_level.title()}: {count} jobs")
        
        # Save files
        print("\n💾 Saving files...")
        files_saved = []
        
        if args.output in ['csv', 'all']:
            csv_file = scraper.save_to_csv(all_jobs)
            files_saved.append(csv_file)
            print(f"   📄 CSV: {os.path.basename(csv_file)}")
        
        if args.output in ['json', 'all']:
            json_file = scraper.save_to_json(all_jobs)
            files_saved.append(json_file)
            print(f"   📄 JSON: {os.path.basename(json_file)}")
        
        if args.output in ['pdf', 'all']:
            pdf_file = scraper.generate_pdf_report(all_jobs)
            files_saved.append(pdf_file)
            print(f"   📄 PDF: {os.path.basename(pdf_file)}")
        
        if args.output in ['all']:
            viz_file = scraper.create_visualization(all_jobs)
            files_saved.append(viz_file)
            print(f"   📊 Visualization: {os.path.basename(viz_file)}")
        
        # Show sample jobs
        print("\n🔍 Sample jobs:")
        for i, job in enumerate(all_jobs[:5]):
            print(f"   {i+1}. {job['title']}")
            print(f"      Company: {job['company']}")
            print(f"      Location: {job['location']}")
            print(f"      Source: {job['source']}")
            print()
        
        if len(all_jobs) > 5:
            print(f"   ... and {len(all_jobs) - 5} more")
        
        # Start web interface if requested
        if args.web:
            print("\n🌐 Starting web interface...")
            
            try:
                port = find_available_port(start_port=5000, max_port=5100)
                print(f"   Open your browser and go to: http://localhost:{port}")
                print("   Press Ctrl+C to stop the web server")
                
                from web_app import app
                app.run(debug=False, host='0.0.0.0', port=port)
            except RuntimeError as e:
                print(f"❌ Error: {e}")
                print("   Please check if any processes are using ports 5000-5099")
            except KeyboardInterrupt:
                print("\n👋 Web server stopped")
            except ImportError:
                print("❌ Web interface not available. Run 'python3 web_app.py' separately.")
    
    else:
        print("❌ No cybersecurity jobs found. Try adjusting your search criteria.")
        sys.exit(1)

if __name__ == '__main__':
    main()