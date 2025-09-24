from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import json
import os
import socket
from datetime import datetime
from job_scraper import CyberSecurityJobScraper, SoftwareEngineeringJobScraper
import pandas as pd
import threading
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables
scraped_jobs = []
scraping_status = {"running": False, "progress": 0, "message": ""}
scraping_thread = None

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

@app.route('/')
def index():
    return render_template('index.html', jobs=scraped_jobs, status=scraping_status)

@app.route('/scrape', methods=['POST'])
def scrape_jobs():
    global scraped_jobs, scraping_status, scraping_thread
    
    # Clear previous results when starting a new search
    scraped_jobs = []
    scraping_status = {"running": False, "progress": 0, "message": ""}  # Reset status
    
    if scraping_status["running"]:
        return jsonify({
            'success': False,
            'message': 'Scraping is already in progress'
        })
    
    data = request.get_json()
    job_type = data.get('job_type', 'cybersecurity')
    keywords = data.get('keywords', '')
    location = data.get('location', 'United States')
    max_pages = data.get('max_pages', 3)
    time_filter = data.get('time_filter', '7d')
    experience_level = data.get('experience_level', 'all')
    sources = data.get('sources', ['Indeed', 'LinkedIn', 'Glassdoor'])
    exclude_citizenship_required = data.get('exclude_citizenship_required', False)
    f1_student = data.get('f1_student', False)
    remove_duplicates = data.get('remove_duplicates', True)
    exclude_easy_apply = data.get('exclude_easy_apply', True)
    use_google_dorks = data.get('use_google_dorks', False)
    serp_api_key = data.get('serp_api_key')
    
    # Store request parameters for the worker function
    request_job_type = job_type
    # Store job type for export functions
    scrape_jobs._last_job_type = job_type
    request_keywords = keywords
    request_location = location
    request_time_filter = time_filter
    request_experience_level = experience_level
    request_sources = sources
    request_exclude_citizenship_required = exclude_citizenship_required
    request_f1_student = f1_student
    request_exclude_easy_apply = exclude_easy_apply
    request_use_google_dorks = use_google_dorks
    request_serp_api_key = serp_api_key
    
    def scrape_worker():
        global scraped_jobs, scraping_status
        
        try:
            scraping_status = {"running": True, "progress": 0, "message": "Initializing scraper..."}
            
            # Choose the appropriate scraper based on job type
            if request_job_type == 'software':
                scraper = SoftwareEngineeringJobScraper()
            else:
                scraper = CyberSecurityJobScraper()
            
            # Use the enhanced scraping method with filters
                # Optionally enable Google Dorks by injecting into sources and env
                sources_to_use = request_sources[:]
                if request_use_google_dorks and 'Google Dorks' not in sources_to_use:
                    sources_to_use.append('Google Dorks')

                if request_serp_api_key:
                    os.environ['SERP_API_KEY'] = request_serp_api_key

                all_jobs = scraper.scrape_all_sources(
                location=request_location,
                time_filter=request_time_filter,
                experience_level=request_experience_level,
                    sources=sources_to_use,
                exclude_citizenship_required=request_exclude_citizenship_required,
                f1_student=request_f1_student,
                exclude_easy_apply=request_exclude_easy_apply,
                keywords=request_keywords
            )
            
            # Save results
            scraping_status["message"] = "Saving results..."
            scraping_status["progress"] = 90
            
            if all_jobs:
                # Save files
                csv_file = scraper.save_to_csv(all_jobs)
                json_file = scraper.save_to_json(all_jobs)
                pdf_file = scraper.generate_pdf_report(all_jobs)
                
                # Try to create visualization (may fail in background thread)
                try:
                    viz_file = scraper.create_visualization(all_jobs)
                except Exception as e:
                    logger.warning(f"Visualization failed: {e}")
                    viz_file = None
                
                scraped_jobs = all_jobs
                scraping_status = {"running": False, "progress": 100, "message": f"Completed! Found {len(all_jobs)} jobs"}
                logger.info(f"Successfully scraped {len(all_jobs)} jobs")
            else:
                scraped_jobs = []
                scraping_status = {"running": False, "progress": 100, "message": "No jobs found"}
                logger.info("No jobs found during scraping")
                
        except Exception as e:
            scraping_status = {"running": False, "progress": 0, "message": f"Error: {str(e)}"}
    
    # Start scraping in background
    scraping_thread = threading.Thread(target=scrape_worker)
    scraping_thread.daemon = True
    scraping_thread.start()
    
    logger.info(f"Scraping request received: location={location}, sources={sources}, f1_student={f1_student}")
    
    return jsonify({
        'success': True,
        'message': 'Scraping started successfully'
    })

@app.route('/status')
def get_status():
    return jsonify(scraping_status)

@app.route('/bookmarks', methods=['GET', 'POST'])
def handle_bookmarks():
    if request.method == 'GET':
        # Return bookmarked jobs
        bookmarked_urls = request.args.getlist('urls')
        if bookmarked_urls:
            bookmarked_jobs = [job for job in scraped_jobs if job.get('url') in bookmarked_urls]
            return jsonify({'success': True, 'jobs': bookmarked_jobs})
        return jsonify({'success': True, 'jobs': []})
    
    elif request.method == 'POST':
        # Save bookmark data (for future use)
        data = request.get_json()
        # Could implement server-side bookmark storage here
        return jsonify({'success': True})

@app.route('/export/<format>')
def export_jobs(format):
    """Export jobs in specified format"""
    if not scraped_jobs:
        return jsonify({'success': False, 'error': 'No jobs to export'})
    
    try:
        # Get the job type from the most recent scraping request
        # Default to cybersecurity if not available
        job_type = getattr(scrape_jobs, '_last_job_type', 'cybersecurity')
        
        if job_type == 'software':
            from job_scraper import SoftwareEngineeringJobScraper
            scraper = SoftwareEngineeringJobScraper()
        else:
            scraper = CyberSecurityJobScraper()
        
        if format == 'csv':
            filename = scraper.save_to_csv(scraped_jobs)
            return jsonify({'success': True, 'filename': filename})
        elif format == 'json':
            filename = scraper.save_to_json(scraped_jobs)
            return jsonify({'success': True, 'filename': filename})
        elif format == 'pdf':
            filename = scraper.generate_pdf_report(scraped_jobs)
            return jsonify({'success': True, 'filename': filename})
        else:
            return jsonify({'success': False, 'error': 'Invalid format'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    """Serve exported files for download"""
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/jobs')
def get_jobs():
    logger.info(f"Jobs endpoint called, returning {len(scraped_jobs)} jobs")
    return jsonify({
        'success': True,
        'jobs': scraped_jobs,
        'count': len(scraped_jobs)
    })

@app.route('/jobs/<int:job_id>')
def get_job(job_id):
    if 0 <= job_id < len(scraped_jobs):
        return jsonify(scraped_jobs[job_id])
    return jsonify({'error': 'Job not found'}), 404

@app.route('/export/csv')
def export_csv():
    if not scraped_jobs:
        return jsonify({'error': 'No jobs to export'}), 400
    
    df = pd.DataFrame(scraped_jobs)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_type = getattr(scrape_jobs, '_last_job_type', 'cybersecurity')
    prefix = "software_engineering" if job_type == 'software' else "cybersecurity"
    filename = f"{prefix}_jobs_{timestamp}.csv"
    filepath = f"/Users/siddh/Masters/Job Scraper/{filename}"
    
    df.to_csv(filepath, index=False)
    
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/export/json')
def export_json():
    if not scraped_jobs:
        return jsonify({'error': 'No jobs to export'}), 400
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_type = getattr(scrape_jobs, '_last_job_type', 'cybersecurity')
    prefix = "software_engineering" if job_type == 'software' else "cybersecurity"
    filename = f"{prefix}_jobs_{timestamp}.json"
    filepath = f"/Users/siddh/Masters/Job Scraper/{filename}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(scraped_jobs, f, indent=2, ensure_ascii=False)
    
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/export/pdf')
def export_pdf():
    if not scraped_jobs:
        return jsonify({'error': 'No jobs to export'}), 400
    
    # Use appropriate scraper based on job type
    job_type = getattr(scrape_jobs, '_last_job_type', 'cybersecurity')
    if job_type == 'software':
        from job_scraper import SoftwareEngineeringJobScraper
        scraper = SoftwareEngineeringJobScraper()
        prefix = "software_engineering"
    else:
        scraper = CyberSecurityJobScraper()
        prefix = "cybersecurity"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_jobs_report_{timestamp}.pdf"
    filepath = scraper.generate_pdf_report(scraped_jobs, filename)
    
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/export/viz')
def export_viz():
    if not scraped_jobs:
        return jsonify({'error': 'No jobs to export'}), 400
    
    try:
        # Use appropriate scraper based on job type
        job_type = getattr(scrape_jobs, '_last_job_type', 'cybersecurity')
        if job_type == 'software':
            from job_scraper import SoftwareEngineeringJobScraper
            scraper = SoftwareEngineeringJobScraper()
            prefix = "software_engineering"
        else:
            scraper = CyberSecurityJobScraper()
            prefix = "cybersecurity"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_jobs_analysis_{timestamp}.png"
        filepath = scraper.create_visualization(scraped_jobs)
        
        if filepath:
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'Failed to create visualization'}), 500
    except Exception as e:
        return jsonify({'error': f'Visualization error: {str(e)}'}), 500

@app.route('/stats')
def get_stats():
    if not scraped_jobs:
        return jsonify({'error': 'No jobs available'}), 400
    
    # Calculate statistics
    sources = {}
    locations = {}
    companies = {}
    
    for job in scraped_jobs:
        source = job.get('source', 'Unknown')
        location = job.get('location', 'Unknown')
        company = job.get('company', 'Unknown')
        
        sources[source] = sources.get(source, 0) + 1
        locations[location] = locations.get(location, 0) + 1
        companies[company] = companies.get(company, 0) + 1
    
    # Top locations and companies
    top_locations = dict(sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10])
    top_companies = dict(sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10])
    
    return jsonify({
        'total_jobs': len(scraped_jobs),
        'sources': sources,
        'top_locations': top_locations,
        'top_companies': top_companies
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Use PORT environment variable for production (Railway, Heroku, etc.)
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🌐 Starting web interface on port {port}")
    if debug_mode:
        print(f"   Open your browser and go to: http://localhost:{port}")
        print(f"   Press Ctrl+C to stop the server")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)