import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from datetime import datetime, timedelta
from fake_useragent import UserAgent
import re
import random
from typing import List, Dict, Optional
import logging
import os
from reportlab.lib.pagesizes import letter, A4
try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from rapidfuzz import fuzz
from urllib.parse import urlparse, parse_qs

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SoftwareEngineeringJobScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # Software engineering-related keywords
        self.software_keywords = [
            'software engineer', 'software developer', 'programmer', 'developer',
            'full stack', 'frontend', 'backend', 'web developer', 'mobile developer',
            'python', 'javascript', 'java', 'react', 'angular', 'vue', 'node.js',
            'machine learning', 'artificial intelligence', 'data science', 'data engineer',
            'devops', 'cloud engineer', 'aws', 'azure', 'kubernetes', 'docker',
            'microservices', 'api', 'rest', 'graphql', 'database', 'sql', 'nosql',
            'agile', 'scrum', 'git', 'ci/cd', 'jenkins', 'terraform', 'ansible',
            'kubernetes', 'docker', 'linux', 'unix', 'system design', 'architecture',
            'senior software engineer', 'lead developer', 'tech lead', 'principal engineer',
            'staff engineer', 'distinguished engineer', 'software architect',
            'junior developer', 'entry level developer', 'associate developer',
            'intern', 'internship', 'co-op', 'graduate', 'new grad', 'entry level',
            'remote', 'work from home', 'hybrid', 'onsite', 'flexible'
        ]
        
        # Job titles variations
        self.job_titles = [
            'software engineer', 'software developer', 'senior software engineer',
            'lead software engineer', 'principal software engineer', 'staff software engineer',
            'distinguished software engineer', 'software architect', 'tech lead',
            'full stack developer', 'frontend developer', 'backend developer',
            'web developer', 'mobile developer', 'ios developer', 'android developer',
            'python developer', 'java developer', 'javascript developer', 'react developer',
            'angular developer', 'vue developer', 'node.js developer', 'php developer',
            'ruby developer', 'go developer', 'rust developer', 'c++ developer',
            'c# developer', '.net developer', 'machine learning engineer', 'data engineer',
            'data scientist', 'ai engineer', 'ml engineer', 'devops engineer',
            'cloud engineer', 'platform engineer', 'infrastructure engineer',
            'site reliability engineer', 'sre', 'cloud architect', 'solutions architect',
            'junior software engineer', 'entry level software engineer', 'associate software engineer',
            'software engineer intern', 'software developer intern', 'engineering intern',
            'graduate software engineer', 'new grad software engineer', 'entry level developer'
        ]

    def is_software_engineering_job(self, title: str, description: str, keywords: str = "") -> bool:
        """Check if a job posting is software engineering-related"""
        text = (title + ' ' + description + ' ' + keywords).lower()
        
        # Check for software engineering keywords
        for keyword in self.software_keywords:
            if keyword.lower() in text:
                return True
        
        # Check for software engineering job titles
        for job_title in self.job_titles:
            if job_title.lower() in text.lower():
                return True
        
        return False

    def canonicalize_text(self, text: str) -> str:
        """Canonicalize text for better matching"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove common punctuation and normalize whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def canonicalize_company(self, company: str) -> str:
        """Canonicalize company name by removing suffixes and common variations"""
        if not company:
            return ""
        
        # Remove common company suffixes
        suffixes = [
            r'\b(inc\.?|incorporated)\b',
            r'\b(llc\.?|limited liability company)\b',
            r'\b(corp\.?|corporation)\b',
            r'\b(ltd\.?|limited)\b',
            r'\b(co\.?|company)\b',
            r'\b(llp\.?|limited liability partnership)\b',
            r'\b(plc\.?|public limited company)\b',
            r'\b(ag\.?|aktiengesellschaft)\b',
            r'\b(gmbh\.?|gesellschaft mit beschränkter haftung)\b'
        ]
        
        text = company.lower()
        for suffix in suffixes:
            text = re.sub(suffix, '', text)
        
        # Clean up and normalize
        text = self.canonicalize_text(text)
        
        return text
    
    def canonicalize_url(self, url: str) -> str:
        """Canonicalize URL by removing tracking parameters and preserving job IDs"""
        if not url:
            return ""
        
        try:
            parsed = urlparse(url)
            
            # Remove common tracking parameters
            tracking_params = [
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                'gclid', 'fbclid', 'msclkid', 'ref', 'source', 'campaign',
                'clickid', 'affiliate', 'partner', 'referrer'
            ]
            
            query_params = parse_qs(parsed.query)
            cleaned_params = {}
            
            # Keep job-related parameters and IDs
            for key, values in query_params.items():
                if any(job_keyword in key.lower() for job_keyword in ['job', 'id', 'req', 'position', 'posting']):
                    cleaned_params[key] = values
                elif key.lower() not in tracking_params:
                    cleaned_params[key] = values
            
            # Rebuild URL
            new_query = '&'.join([f"{k}={v[0]}" for k, v in cleaned_params.items()])
            canonical_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if new_query:
                canonical_url += f"?{new_query}"
            
            return canonical_url
            
        except Exception as e:
            logger.warning(f"Error canonicalizing URL {url}: {e}")
            return url
    
    def remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Advanced deduplication with canonicalization and fuzzy matching"""
        if not jobs:
            return jobs
        
        unique_jobs = []

        for i, job in enumerate(jobs):
            is_duplicate = False
            
            # Canonicalize current job data
            canonical_title = self.canonicalize_text(job.get('title', ''))
            canonical_company = self.canonicalize_company(job.get('company', ''))
            canonical_url = self.canonicalize_url(job.get('url', ''))
            
            # Update job with canonical data
            job['canonical_title'] = canonical_title
            job['canonical_company'] = canonical_company
            job['canonical_url'] = canonical_url
            
            # Check against already processed jobs
            for existing_job in unique_jobs:
                existing_title = existing_job.get('canonical_title', '')
                existing_company = existing_job.get('canonical_company', '')
                
                # Exact match on canonical data
                if (canonical_title == existing_title and 
                    canonical_company == existing_company):
                    is_duplicate = True
                    break
                
                # Fuzzy match on title + company
                if canonical_title and canonical_company and existing_title and existing_company:
                    # Combine title and company for fuzzy matching
                    current_combined = f"{canonical_title} {canonical_company}"
                    existing_combined = f"{existing_title} {existing_company}"
                    
                    # Use token_set_ratio for better fuzzy matching
                    similarity = fuzz.token_set_ratio(current_combined, existing_combined)
                    
                    if similarity >= 92:
                        is_duplicate = True
                        logger.debug(f"Fuzzy duplicate found: '{current_combined}' vs '{existing_combined}' (similarity: {similarity}%)")
                        break
            
            if not is_duplicate:
                unique_jobs.append(job)
        
        logger.info(f"Removed {len(jobs) - len(unique_jobs)} duplicates using advanced deduplication")
        return unique_jobs

    def classify_citizenship_clearance(self, text: str) -> Dict[str, bool]:
        """Classify citizenship and clearance requirements using advanced keyword matching"""
        text_lower = text.lower()
        
        # Enhanced citizenship/clearance keywords
        citizenship_keywords = [
            # Direct citizenship requirements
            'us citizen', 'u.s. citizen', 'united states citizen',
            'us citizenship', 'u.s. citizenship', 'united states citizenship',
            'must be a us citizen', 'requires us citizenship',
            'us citizen only', 'citizenship required',
            
            # Security clearance requirements
            'eligible for security clearance', 'security clearance required',
            'security clearance', 'government clearance', 'public trust',
            'background check', 'federal clearance', 'defense clearance',
            'top secret', 'secret clearance', 'confidential clearance',
            'government contractor', 'department of defense', 'dod',
            'federal government', 'national security',
            
            # Exclusion keywords
            'no sponsorship', 'no visa sponsorship', 'citizens only',
            'us citizens only', 'must be us citizen'
        ]
        
        # Sponsorship/OPT-CPT friendly keywords
        sponsorship_keywords = [
            # Explicit sponsorship mentions
            'sponsor', 'sponsorship', 'h1b', 'h-1b', 'visa sponsorship',
            'international', 'global', 'remote', 'work from home',
            'f1', 'opt', 'cpt', 'stem opt', 'optional practical training',
            'diversity', 'inclusive', 'equal opportunity',
            
            # Positive indicators
            'sponsor h1b', 'h1b sponsorship', 'visa support',
            'international candidates welcome', 'global talent',
            'remote work', 'work from anywhere'
        ]
        
        # Calculate scores
        citizenship_score = sum(1 for keyword in citizenship_keywords if keyword in text_lower)
        sponsorship_score = sum(1 for keyword in sponsorship_keywords if keyword in text_lower)
        
        # Determine classifications
        requires_citizenship = citizenship_score > 0
        is_sponsorship_friendly = sponsorship_score > 0
        
        # Override logic: if explicit citizenship requirement, override sponsorship
        if requires_citizenship and any(keyword in text_lower for keyword in ['citizens only', 'us citizens only', 'no sponsorship']):
            is_sponsorship_friendly = False
        
        return {
            'requires_us_citizenship': requires_citizenship,
            'requires_security_clearance': any(keyword in text_lower for keyword in [
                'security clearance', 'government clearance', 'top secret', 'secret clearance'
            ]),
            'is_sponsorship_friendly': is_sponsorship_friendly,
            'is_f1_student_friendly': is_sponsorship_friendly and not requires_citizenship,
            'citizenship_score': citizenship_score,
            'sponsorship_score': sponsorship_score
        }
    
    def filter_citizenship_clearance(self, jobs: List[Dict], exclude_citizenship_required: bool = False) -> List[Dict]:
        """Advanced citizenship and clearance filtering with intelligent classification"""
        for job in jobs:
            # Combine title and description for analysis
            full_text = f"{job.get('title', '')} {job.get('description', '')}"
            
            # Get intelligent classifications
            classifications = self.classify_citizenship_clearance(full_text)
            
            # Update job with all classification data
            job.update(classifications)
            
            # Add UI-friendly tags
            tags = []
            if job['requires_us_citizenship']:
                tags.append('US Citizenship Required')
            if job['requires_security_clearance']:
                tags.append('Security Clearance Required')
            if job['is_sponsorship_friendly']:
                tags.append('Sponsorship Friendly')
            if job['is_f1_student_friendly']:
                tags.append('F1 Student Friendly')
            
            job['classification_tags'] = tags
        
        # Filter based on requirement
        if exclude_citizenship_required:
            # Return jobs that do NOT require citizenship
            filtered_jobs = [job for job in jobs if not job['requires_us_citizenship']]
            logger.info(f"Filtered out {len(jobs) - len(filtered_jobs)} jobs requiring citizenship")
            return filtered_jobs
        else:
            # Return all jobs with classification data
            return jobs

    def filter_f1_student_friendly(self, jobs: List[Dict], f1_student: bool = False) -> List[Dict]:
        """Filter jobs that are F1 student friendly using intelligent classification"""
        if not f1_student:
            return jobs
        
        # Use the intelligent classification already performed
        # Jobs should already have 'is_f1_student_friendly' field from filter_citizenship_clearance
        filtered_jobs = [job for job in jobs if job.get('is_f1_student_friendly', False)]
        
        logger.info(f"F1 student filter: kept {len(filtered_jobs)} out of {len(jobs)} jobs")
        return filtered_jobs

    def scrape_indeed(self, location: str = "United States", max_pages: int = 5, time_filter: str = "7", experience_level: str = "all", keywords: str = "") -> List[Dict]:
        """Scrape software engineering jobs from Indeed with enhanced filtering"""
        jobs = []
        base_url = "https://www.indeed.com/jobs"
        
        # Map time filters to Indeed's fromage parameter
        time_mapping = {
            "0.5": "1",  # 12 hours -> 1 day (closest option)
            "12h": "1",
            "1": "1",    # 24 hours
            "24h": "1",
            "3": "3",    # 3 days
            "3d": "3", 
            "7": "7",    # 7 days
            "7d": "7",
            "14": "14",  # 14 days
            "14d": "14",
            "30": "30",  # 30 days
            "30d": "30"
        }
        fromage = time_mapping.get(time_filter, "7")
        
        # Map experience levels to Indeed's explvl parameter
        exp_mapping = {
            "entry": "explvl%3AENTRY_LEVEL",
            "mid": "explvl%3AMID_LEVEL", 
            "senior": "explvl%3ASENIOR_LEVEL",
            "internship": "explvl%3AINTERNSHIP"
        }
        
        for page in range(max_pages):
            try:
                # Build query with experience filter
                base_query = 'software engineer OR "software developer" OR "full stack" OR "frontend" OR "backend" OR "web developer"'
                if keywords:
                    base_query += f' OR {keywords}'
                
                if experience_level != "all" and experience_level in exp_mapping:
                    query = f"{base_query} {exp_mapping[experience_level]}"
                else:
                    query = base_query
                
                params = {
                    'q': query,
                    'l': location,
                    'start': page * 10,
                    'sort': 'date',
                    'fromage': fromage
                }
                
                response = self.session.get(base_url, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2', class_='jobTitle')
                        if not title_elem:
                            continue
                            
                        title = title_elem.get_text(strip=True)
                        
                        # Try multiple selectors for company name (Indeed changes their HTML structure)
                        company = "Unknown"
                        company_selectors = [
                            'span[data-testid="company-name"]',
                            'span.companyName',
                            '.companyName',
                            '[data-testid="company-name"]',
                            'span[title]',
                            'div[data-testid="company-name"]'
                        ]
                        
                        for selector in company_selectors:
                            company_elem = card.select_one(selector)
                            if company_elem:
                                company = company_elem.get_text(strip=True)
                                if company and company != "Unknown":
                                    break
                        
                        # Fallback: look for any span with company-like content
                        if company == "Unknown":
                            spans = card.find_all('span')
                            for span in spans:
                                text = span.get_text(strip=True)
                                if text and len(text) > 2 and len(text) < 50 and not any(char.isdigit() for char in text):
                                    company = text
                                    break
                        
                        location_elem = card.find('div', class_='companyLocation')
                        job_location = location_elem.get_text(strip=True) if location_elem else location
                        
                        # Check for sponsored job
                        sponsored = "Sponsored" in card.get_text() or "sponsored" in card.get_text()
                        
                        # Get job description link
                        link_elem = title_elem.find('a')
                        if link_elem:
                            job_url = "https://www.indeed.com" + link_elem['href']
                            
                            # Get job description
                            try:
                                desc_response = self.session.get(job_url)
                                desc_soup = BeautifulSoup(desc_response.content, 'html.parser')
                                desc_elem = desc_soup.find('div', class_='jobsearch-jobDescriptionText')
                                description = desc_elem.get_text(strip=True) if desc_elem else ""
                            except Exception:
                                description = ""
                        else:
                            description = ""
                            job_url = ""
                        
                        # Check if it's a software engineering job
                        if self.is_software_engineering_job(title, description, keywords):
                            job_data = {
                                'title': title,
                                'company': company,
                                'location': job_location,
                                'description': description[:1000] + "..." if len(description) > 1000 else description,
                                'url': job_url,
                                'source': 'Indeed',
                                'scraped_at': datetime.now().isoformat(),
                                'posted_date': self._extract_date(card),
                                'sponsored': sponsored,
                                'experience_level': experience_level
                            }
                            jobs.append(job_data)
                            
                    except Exception as e:
                        logger.warning(f"Error parsing job card: {e}")
                        continue
                
                logger.info(f"Scraped page {page + 1} from Indeed")
                time.sleep(2)  # Be respectful to the server
                
            except Exception as e:
                logger.error(f"Error scraping Indeed page {page + 1}: {e}")
                continue
        
        return jobs

    def scrape_linkedin_jobs(self, location: str = "United States", max_pages: int = 3, time_filter: str = "7", experience_level: str = "all", exclude_easy_apply: bool = True, keywords: str = "") -> List[Dict]:
        """Scrape software engineering jobs from LinkedIn with enhanced filtering"""
        jobs = []
        
        try:
            search_terms = [
                'software engineer',
                'software developer',
                'full stack developer',
                'frontend developer',
                'backend developer',
                'web developer'
            ]
            
            if keywords:
                search_terms.extend([term.strip() for term in keywords.split(',')])
            
            # Map time filters to LinkedIn's f_TPR parameter
            time_mapping = {
                "0.5": "r43200",   # 12 hours
                "12h": "r43200",
                "1": "r86400",     # 24 hours
                "24h": "r86400",
                "3": "r259200",    # 3 days
                "3d": "r259200", 
                "7": "r604800",    # 7 days
                "7d": "r604800",
                "14": "r1209600",  # 14 days
                "14d": "r1209600",
                "30": "r2592000",  # 30 days
                "30d": "r2592000"
            }
            tpr_filter = time_mapping.get(time_filter, "r604800")
            
            # Map experience levels to LinkedIn's f_E parameter
            exp_mapping = {
                "entry": "2",
                "mid": "3", 
                "senior": "4",
                "internship": "1"
            }
            
            for term in search_terms:
                # Build URL with filters
                base_url = f"https://www.linkedin.com/jobs/search/?keywords={term}&location={location}&f_TPR={tpr_filter}"
                if experience_level != "all" and experience_level in exp_mapping:
                    base_url += f"&f_E={exp_mapping[experience_level]}"
                
                response = self.session.get(base_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # LinkedIn structure - this may need adjustment based on current site structure
                    job_listings = soup.find_all('div', class_='job-search-card')
                    
                    for listing in job_listings[:15]:  # Limit to avoid rate limiting
                        try:
                            title_elem = listing.find('h3', class_='base-search-card__title')
                            title = title_elem.get_text(strip=True) if title_elem else ""
                            
                            company_elem = listing.find('h4', class_='base-search-card__subtitle')
                            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                            
                            location_elem = listing.find('span', class_='job-search-card__location')
                            job_location = location_elem.get_text(strip=True) if location_elem else location
                            
                            link_elem = listing.find('a')
                            job_url = link_elem['href'] if link_elem else ""
                            
                            # Check for sponsored job
                            sponsored = "sponsored" in listing.get_text().lower()
                            
                            # Check for Easy Apply job (filter these out if exclude_easy_apply is True)
                            job_text = listing.get_text().lower()
                            is_easy_apply = any(keyword in job_text for keyword in [
                                "easy apply", "quick apply", "apply now", "one-click apply", 
                                "instant apply", "apply instantly", "fast apply", "in easy apply"
                            ])
                            
                            # Also check for Easy Apply button or icon in the HTML
                            easy_apply_buttons = listing.find_all(['button', 'span', 'div'], 
                                string=lambda text: text and any(keyword in text.lower() for keyword in [
                                    "easy apply", "quick apply", "apply now", "in easy apply"
                                ]))
                            
                            if easy_apply_buttons:
                                is_easy_apply = True
                            
                            # Additional check for LinkedIn's specific Easy Apply indicators
                            if 'linkedin' in job_url.lower():
                                # Check if the job URL contains Easy Apply indicators
                                if any(indicator in job_url.lower() for indicator in ['easy-apply', 'quick-apply']):
                                    is_easy_apply = True
                            
                            # Check for Easy Apply in button text or aria-labels
                            easy_apply_elements = listing.find_all(['button', 'span', 'div'], 
                                attrs={'aria-label': lambda x: x and any(keyword in x.lower() for keyword in [
                                    "easy apply", "quick apply", "apply now", "in easy apply"
                                ])})
                            
                            if easy_apply_elements:
                                is_easy_apply = True
                            
                            # Note: We don't skip Easy Apply jobs here anymore
                            # They will be categorized and can be filtered in the frontend
                            
                            if title and self.is_software_engineering_job(title, "", keywords):
                                # Determine source based on company and Easy Apply status
                                if company.lower() in ['lensa', 'dice']:
                                    source = 'Staffing'
                                    logger.info(f"👥 Staffing job detected: {title} at {company}")
                                elif is_easy_apply:
                                    source = 'Easy Apply'
                                    logger.info(f"🎯 Easy Apply job detected: {title} at {company}")
                                else:
                                    # IMPROVED Easy Apply detection
                                    is_actually_easy_apply = False
                                    
                                    # Method 1: Check the entire job listing HTML for Easy Apply indicators
                                    job_html = str(listing)
                                    easy_apply_keywords = [
                                        'easy apply', 'quick apply', 'apply now', 'one-click apply',
                                        'instant apply', 'apply instantly', 'fast apply', 'in easy apply',
                                        'easyapply', 'quickapply', 'applynow', 'easy-apply', 'quick-apply'
                                    ]
                                    
                                    # Check if any Easy Apply keywords are in the HTML
                                    for keyword in easy_apply_keywords:
                                        if keyword in job_html.lower():
                                            is_actually_easy_apply = True
                                            logger.info(f"🔍 Easy Apply detected via keyword '{keyword}': {title}")
                                            break
                                    
                                    # Method 2: Check for LinkedIn's specific Easy Apply button patterns
                                    if not is_actually_easy_apply and 'linkedin' in job_url.lower():
                                        # Look for buttons with Easy Apply text
                                        buttons = listing.find_all(['button', 'span', 'div', 'a'])
                                        for button in buttons:
                                            button_text = button.get_text().lower().strip()
                                            if any(keyword in button_text for keyword in easy_apply_keywords):
                                                is_actually_easy_apply = True
                                                logger.info(f"🔍 Easy Apply detected via button text '{button_text}': {title}")
                                                break
                                    
                                    # Method 3: Check for LinkedIn's Easy Apply button classes and attributes
                                    if not is_actually_easy_apply and 'linkedin' in job_url.lower():
                                        # Look for elements with Easy Apply related classes or attributes
                                        easy_apply_elements = listing.find_all(attrs={
                                            'class': lambda x: x and any(
                                                'easy' in str(x).lower() or 'apply' in str(x).lower() or 'quick' in str(x).lower()
                                                for x in (x if isinstance(x, list) else [x])
                                            )
                                        })
                                        
                                        if easy_apply_elements:
                                            # Double-check that these elements contain Easy Apply text
                                            for element in easy_apply_elements:
                                                element_text = element.get_text().lower()
                                                if any(keyword in element_text for keyword in easy_apply_keywords):
                                                    is_actually_easy_apply = True
                                                    logger.info(f"🔍 Easy Apply detected via LinkedIn element: {title}")
                                                    break
                                    
                                    # Method 4: Check for specific LinkedIn Easy Apply patterns in the URL
                                    if not is_actually_easy_apply and 'linkedin' in job_url.lower():
                                        url_indicators = ['easy-apply', 'quick-apply', 'easyapply', 'quickapply']
                                        if any(indicator in job_url.lower() for indicator in url_indicators):
                                            is_actually_easy_apply = True
                                            logger.info(f"🔍 Easy Apply detected via URL: {title}")
                                    
                                    # Determine final source - All LinkedIn jobs together
                                    if company.lower() in ['lensa', 'dice']:
                                        source = 'Staffing'
                                        logger.info(f"👥 Staffing job detected: {title} at {company}")
                                    else:
                                        source = 'LinkedIn'
                                        logger.info(f"💼 LinkedIn job: {title} at {company}")
                                
                                job_data = {
                                    'title': title,
                                    'company': company,
                                    'location': job_location,
                                    'description': f"Software engineering position at {company}. Click link for full details.",
                                    'url': job_url,
                                    'source': source,
                                    'scraped_at': datetime.now().isoformat(),
                                    'posted_date': datetime.now().isoformat(),
                                    'sponsored': sponsored,
                                    'experience_level': experience_level,
                                    'easy_apply': is_easy_apply
                                }
                                jobs.append(job_data)
                                
                        except Exception as e:
                            logger.warning(f"Error parsing LinkedIn job: {e}")
                            continue
                
                time.sleep(3)  # Longer delay for LinkedIn
                
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
        
        return jobs

    def scrape_all_sources(self, location: str = "United States", time_filter: str = "7", experience_level: str = "all", sources: List[str] = None, exclude_citizenship_required: bool = False, f1_student: bool = False, exclude_easy_apply: bool = True, keywords: str = "") -> List[Dict]:
        """Scrape jobs from all sources with advanced filtering and intelligent classification"""
        all_jobs = []
        
        # Default to all sources if none specified
        if sources is None:
            sources = ['Indeed', 'LinkedIn', 'Glassdoor', 'ZipRecruiter', 'Dice', 'Wellfound']
        
        logger.info(f"Starting software engineering job scraping from {', '.join(sources)}...")
        logger.info(f"Filters: Easy Apply excluded={exclude_easy_apply}, Exclude Citizenship Required={exclude_citizenship_required}, F1 Student={f1_student}")
        logger.info(f"Keywords: {keywords}")
        
        # Scrape from Indeed
        if 'Indeed' in sources:
            logger.info("🔍 Scraping Indeed...")
            indeed_jobs = self.scrape_indeed(location, time_filter=time_filter, experience_level=experience_level, keywords=keywords)
            logger.info(f"✅ Found {len(indeed_jobs)} jobs from Indeed")
            all_jobs.extend(indeed_jobs)
        
        # Scrape from LinkedIn
        if 'LinkedIn' in sources:
            logger.info("🔍 Scraping LinkedIn...")
            linkedin_jobs = self.scrape_linkedin_jobs(location, time_filter=time_filter, experience_level=experience_level, exclude_easy_apply=exclude_easy_apply, keywords=keywords)
            logger.info(f"✅ Found {len(linkedin_jobs)} jobs from LinkedIn")
            all_jobs.extend(linkedin_jobs)
        
        # Advanced deduplication with canonicalization and fuzzy matching
        logger.info(f"Total jobs scraped before deduplication: {len(all_jobs)}")
        all_jobs = self.remove_duplicates(all_jobs)
        logger.info(f"Total jobs after deduplication: {len(all_jobs)}")
        
        # Apply intelligent citizenship and clearance classification
        all_jobs = self.filter_citizenship_clearance(all_jobs, exclude_citizenship_required=exclude_citizenship_required)
        
        # Apply F1 student filtering if requested
        if f1_student:
            all_jobs = self.filter_f1_student_friendly(all_jobs, f1_student=True)
            logger.info(f"Total jobs after F1 student filter: {len(all_jobs)}")
        
        logger.info(f"Final total jobs: {len(all_jobs)}")
        return all_jobs

    def save_to_csv(self, jobs: List[Dict], filename: str = None) -> str:
        """Save jobs to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"software_engineering_jobs_{timestamp}.csv"
        
        df = pd.DataFrame(jobs)
        filepath = f"/Users/siddh/Masters/Job Scraper/{filename}"
        df.to_csv(filepath, index=False)
        
        logger.info(f"Jobs saved to {filepath}")
        return filepath

    def save_to_json(self, jobs: List[Dict], filename: str = None) -> str:
        """Save jobs to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"software_engineering_jobs_{timestamp}.json"
        
        filepath = f"/Users/siddh/Masters/Job Scraper/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Jobs saved to {filepath}")
        return filepath

    def generate_pdf_report(self, jobs: List[Dict], filename: str = None) -> str:
        """Generate a comprehensive PDF report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"software_engineering_jobs_report_{timestamp}.pdf"
        
        filepath = f"/Users/siddh/Masters/Job Scraper/{filename}"
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Content
        story = []
        
        # Title
        story.append(Paragraph("Software Engineering Jobs Report", title_style))
        story.append(Spacer(1, 12))
        
        # Summary
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Paragraph(f"Total Jobs Found: {len(jobs)}", styles['Normal']))
        
        # Source breakdown
        sources = {}
        for job in jobs:
            source = job['source']
            sources[source] = sources.get(source, 0) + 1
        
        story.append(Paragraph("Jobs by Source:", styles['Normal']))
        for source, count in sources.items():
            story.append(Paragraph(f"• {source}: {count} jobs", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Top companies
        companies = {}
        for job in jobs:
            company = job['company']
            companies[company] = companies.get(company, 0) + 1
        
        top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]
        
        story.append(Paragraph("Top Companies Hiring:", heading_style))
        for company, count in top_companies:
            story.append(Paragraph(f"• {company}: {count} positions", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Job listings
        story.append(Paragraph("Job Listings", heading_style))
        
        # Create table for job listings with enhanced information
        table_data = [['Title', 'Company', 'Location', 'Source', 'Sponsored']]
        
        for job in jobs[:50]:  # Limit to first 50 jobs for readability
            sponsored_text = "Yes" if job.get('sponsored', False) else "No"
            table_data.append([
                job['title'][:45] + "..." if len(job['title']) > 45 else job['title'],
                job['company'][:25] + "..." if len(job['company']) > 25 else job['company'],
                job['location'][:20] + "..." if len(job['location']) > 20 else job['location'],
                job['source'],
                sponsored_text
            ])
        
        job_table = Table(table_data)
        job_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(job_table)
        
        # Add job links section
        story.append(Spacer(1, 20))
        story.append(Paragraph("Job Application Links", heading_style))
        
        for i, job in enumerate(jobs[:20], 1):  # Show first 20 job links
            if job.get('url'):
                link_text = f"{i}. {job['title']} at {job['company']}"
                story.append(Paragraph(link_text, styles['Normal']))
                story.append(Paragraph(f"   Link: {job['url']}", styles['Normal']))
                story.append(Spacer(1, 8))
        
        if len(jobs) > 20:
            story.append(Paragraph(f"... and {len(jobs) - 20} more jobs. Check the CSV/JSON files for complete links.", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"PDF report saved to {filepath}")
        return filepath

    def create_visualization(self, jobs: List[Dict]) -> str:
        """Create visualization charts for the jobs data"""
        try:
            if not jobs:
                return None
            
            # Prepare data
            sources = {}
            locations = {}
            companies = {}
            
            for job in jobs:
                # Source data
                source = job.get('source', 'Unknown')
                sources[source] = sources.get(source, 0) + 1
                
                # Location data
                location = job.get('location', 'Unknown')
                # Extract state/city from location
                if ',' in location:
                    state = location.split(',')[-1].strip()
                    locations[state] = locations.get(state, 0) + 1
                else:
                    locations[location] = locations.get(location, 0) + 1
                
                # Company data
                company = job.get('company', 'Unknown')
                companies[company] = companies.get(company, 0) + 1
            
            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Software Engineering Jobs Analysis', fontsize=16, fontweight='bold')
            
            # Source distribution
            if sources:
                ax1.pie(sources.values(), labels=sources.keys(), autopct='%1.1f%%', startangle=90)
                ax1.set_title('Jobs by Source')
            else:
                ax1.text(0.5, 0.5, 'No source data', ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('Jobs by Source')
            
            # Top locations
            top_locations = dict(sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10])
            if top_locations:
                ax2.barh(list(top_locations.keys()), list(top_locations.values()))
                ax2.set_title('Top Locations')
                ax2.set_xlabel('Number of Jobs')
            else:
                ax2.text(0.5, 0.5, 'No location data', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Top Locations')
            
            # Top companies
            top_companies = dict(sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10])
            if top_companies:
                ax3.bar(range(len(top_companies)), list(top_companies.values()))
                ax3.set_xticks(range(len(top_companies)))
                ax3.set_xticklabels(list(top_companies.keys()), rotation=45, ha='right')
                ax3.set_title('Top Companies')
                ax3.set_ylabel('Number of Jobs')
            else:
                ax3.text(0.5, 0.5, 'No company data', ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('Top Companies')
            
            # Jobs over time (simulated)
            ax4.plot(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], [5, 8, 12, 15, 10])
            ax4.set_title('Job Postings Trend')
            ax4.set_ylabel('Number of Jobs')
            
            plt.tight_layout()
            
            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_filename = f"/Users/siddh/Masters/Job Scraper/software_engineering_jobs_analysis_{timestamp}.png"
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Visualization saved to {plot_filename}")
            return plot_filename
            
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return None

    def _extract_date(self, job_card) -> str:
        """Extract posted date from job card"""
        try:
            date_elem = job_card.find('span', class_='date')
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                # Parse relative dates like "2 days ago"
                if 'day' in date_text:
                    days = int(re.search(r'(\d+)', date_text).group(1))
                    return (datetime.now() - timedelta(days=days)).isoformat()
                elif 'hour' in date_text:
                    return datetime.now().isoformat()
            return datetime.now().isoformat()
        except Exception:
            return datetime.now().isoformat()


class CyberSecurityJobScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # Cybersecurity-related keywords (enhanced with junior positions)
        self.cyber_keywords = [
            'cybersecurity', 'cyber security', 'information security', 'infosec',
            'security engineer', 'security analyst', 'penetration tester', 'pen tester',
            'security consultant', 'SOC analyst', 'incident response', 'threat hunter',
            'vulnerability assessment', 'security architect', 'CISO', 'security manager',
            'network security', 'application security', 'cloud security', 'devsecops',
            'security operations', 'SIEM', 'firewall', 'intrusion detection',
            'malware analysis', 'forensics', 'compliance', 'GDPR', 'HIPAA', 'SOX',
            'ISO 27001', 'NIST', 'CISSP', 'CISM', 'CEH', 'Security+', 'CISA',
            'security administrator', 'security specialist', 'security coordinator',
            'risk analyst', 'security auditor', 'security operations center',
            'threat intelligence', 'vulnerability management', 'security monitoring',
            'GRC', 'governance risk compliance', 'security awareness', 'red team',
            'blue team', 'purple team', 'threat hunting', 'DFIR', 'digital forensics',
            'identity and access management', 'IAM', 'zero trust', 'endpoint security',
            'data loss prevention', 'DLP', 'security awareness training',
            # Junior-level keywords
            'junior security', 'entry level security', 'associate security', 'trainee security',
            'security trainee', 'security intern', 'cybersecurity intern', 'security apprentice',
            'level 1 security', 'l1 security', 'security associate', 'junior analyst',
            'entry level analyst', 'associate analyst', 'security coordinator', 'security assistant'
        ]
        
        # Job titles variations (enhanced with junior positions)
        self.job_titles = [
            'security engineer', 'security analyst', 'cybersecurity engineer',
            'information security analyst', 'security consultant', 'penetration tester',
            'security architect', 'SOC analyst', 'SOC engineer', 'SOC manager',
            'incident response analyst', 'threat intelligence analyst', 'security operations center',
            'vulnerability assessment specialist', 'security manager',
            'chief information security officer', 'security administrator',
            'security specialist', 'security coordinator', 'risk analyst',
            'security auditor', 'security technician', 'cybersecurity specialist',
            'information security specialist', 'network security engineer',
            'application security engineer', 'cloud security engineer',
            'security operations analyst', 'malware analyst', 'forensic analyst',
            'compliance analyst', 'GRC analyst', 'security trainer',
            'identity and access management specialist', 'IAM specialist',
            'security awareness specialist', 'threat hunter', 'red team analyst',
            'blue team analyst', 'security researcher',
            # Junior-level titles
            'junior security engineer', 'junior security analyst', 'junior SOC analyst',
            'junior cybersecurity engineer', 'junior information security analyst',
            'junior security consultant', 'junior penetration tester', 'junior security architect',
            'junior incident response analyst', 'junior threat intelligence analyst',
            'junior security administrator', 'junior security specialist',
            'junior security coordinator', 'junior risk analyst', 'junior security auditor',
            'junior cybersecurity specialist', 'junior network security engineer',
            'junior application security engineer', 'junior cloud security engineer',
            'junior security operations analyst', 'junior malware analyst',
            'junior forensic analyst', 'junior compliance analyst', 'junior GRC analyst',
            'junior IAM specialist', 'junior threat hunter', 'junior security researcher',
            'entry level security engineer', 'entry level security analyst', 'entry level SOC analyst',
            'associate security engineer', 'associate security analyst', 'associate SOC analyst',
            'security engineer intern', 'security analyst intern', 'SOC analyst intern',
            'cybersecurity engineer intern', 'information security intern', 'security consultant intern',
            'security architect intern', 'penetration tester intern', 'incident response intern'
        ]

    def is_cybersecurity_job(self, title: str, description: str) -> bool:
        """Check if a job posting is cybersecurity-related"""
        text = (title + ' ' + description).lower()
        
        # Check for cybersecurity keywords
        for keyword in self.cyber_keywords:
            if keyword.lower() in text:
                return True
        
        # Check for security-related job titles
        for job_title in self.job_titles:
            if job_title.lower() in text.lower():
                return True
        
        return False

    def canonicalize_text(self, text: str) -> str:
        """Canonicalize text for better matching"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove common punctuation and normalize whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def canonicalize_company(self, company: str) -> str:
        """Canonicalize company name by removing suffixes and common variations"""
        if not company:
            return ""
        
        # Remove common company suffixes
        suffixes = [
            r'\b(inc\.?|incorporated)\b',
            r'\b(llc\.?|limited liability company)\b',
            r'\b(corp\.?|corporation)\b',
            r'\b(ltd\.?|limited)\b',
            r'\b(co\.?|company)\b',
            r'\b(llp\.?|limited liability partnership)\b',
            r'\b(plc\.?|public limited company)\b',
            r'\b(ag\.?|aktiengesellschaft)\b',
            r'\b(gmbh\.?|gesellschaft mit beschränkter haftung)\b'
        ]
        
        text = company.lower()
        for suffix in suffixes:
            text = re.sub(suffix, '', text)
        
        # Clean up and normalize
        text = self.canonicalize_text(text)
        
        return text
    
    def canonicalize_url(self, url: str) -> str:
        """Canonicalize URL by removing tracking parameters and preserving job IDs"""
        if not url:
            return ""
        
        try:
            parsed = urlparse(url)
            
            # Remove common tracking parameters
            tracking_params = [
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                'gclid', 'fbclid', 'msclkid', 'ref', 'source', 'campaign',
                'clickid', 'affiliate', 'partner', 'referrer'
            ]
            
            query_params = parse_qs(parsed.query)
            cleaned_params = {}
            
            # Keep job-related parameters and IDs
            for key, values in query_params.items():
                if any(job_keyword in key.lower() for job_keyword in ['job', 'id', 'req', 'position', 'posting']):
                    cleaned_params[key] = values
                elif key.lower() not in tracking_params:
                    cleaned_params[key] = values
            
            # Rebuild URL
            new_query = '&'.join([f"{k}={v[0]}" for k, v in cleaned_params.items()])
            canonical_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if new_query:
                canonical_url += f"?{new_query}"
            
            return canonical_url
            
        except Exception as e:
            logger.warning(f"Error canonicalizing URL {url}: {e}")
            return url
    
    def remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Advanced deduplication with canonicalization and fuzzy matching"""
        if not jobs:
            return jobs
        
        unique_jobs = []

        for i, job in enumerate(jobs):
            is_duplicate = False
            
            # Canonicalize current job data
            canonical_title = self.canonicalize_text(job.get('title', ''))
            canonical_company = self.canonicalize_company(job.get('company', ''))
            canonical_url = self.canonicalize_url(job.get('url', ''))
            
            # Update job with canonical data
            job['canonical_title'] = canonical_title
            job['canonical_company'] = canonical_company
            job['canonical_url'] = canonical_url
            
            # Check against already processed jobs
            for existing_job in unique_jobs:
                existing_title = existing_job.get('canonical_title', '')
                existing_company = existing_job.get('canonical_company', '')
                
                # Exact match on canonical data
                if (canonical_title == existing_title and 
                    canonical_company == existing_company):
                    is_duplicate = True
                    break
                
                # Fuzzy match on title + company
                if canonical_title and canonical_company and existing_title and existing_company:
                    # Combine title and company for fuzzy matching
                    current_combined = f"{canonical_title} {canonical_company}"
                    existing_combined = f"{existing_title} {existing_company}"
                    
                    # Use token_set_ratio for better fuzzy matching
                    similarity = fuzz.token_set_ratio(current_combined, existing_combined)
                    
                    if similarity >= 92:
                        is_duplicate = True
                        logger.debug(f"Fuzzy duplicate found: '{current_combined}' vs '{existing_combined}' (similarity: {similarity}%)")
                        break
            
            if not is_duplicate:
                unique_jobs.append(job)
        
        logger.info(f"Removed {len(jobs) - len(unique_jobs)} duplicates using advanced deduplication")
        return unique_jobs

    def classify_citizenship_clearance(self, text: str) -> Dict[str, bool]:
        """Classify citizenship and clearance requirements using advanced keyword matching"""
        text_lower = text.lower()
        
        # Enhanced citizenship/clearance keywords
        citizenship_keywords = [
            # Direct citizenship requirements
            'us citizen', 'u.s. citizen', 'united states citizen',
            'us citizenship', 'u.s. citizenship', 'united states citizenship',
            'must be a us citizen', 'requires us citizenship',
            'us citizen only', 'citizenship required',
            
            # Security clearance requirements
            'eligible for security clearance', 'security clearance required',
            'security clearance', 'government clearance', 'public trust',
            'background check', 'federal clearance', 'defense clearance',
            'top secret', 'secret clearance', 'confidential clearance',
            'government contractor', 'department of defense', 'dod',
            'federal government', 'national security',
            
            # Exclusion keywords
            'no sponsorship', 'no visa sponsorship', 'citizens only',
            'us citizens only', 'must be us citizen'
        ]
        
        # Sponsorship/OPT-CPT friendly keywords
        sponsorship_keywords = [
            # Explicit sponsorship mentions
            'sponsor', 'sponsorship', 'h1b', 'h-1b', 'visa sponsorship',
            'international', 'global', 'remote', 'work from home',
            'f1', 'opt', 'cpt', 'stem opt', 'optional practical training',
            'diversity', 'inclusive', 'equal opportunity',
            
            # Positive indicators
            'sponsor h1b', 'h1b sponsorship', 'visa support',
            'international candidates welcome', 'global talent',
            'remote work', 'work from anywhere'
        ]
        
        # Calculate scores
        citizenship_score = sum(1 for keyword in citizenship_keywords if keyword in text_lower)
        sponsorship_score = sum(1 for keyword in sponsorship_keywords if keyword in text_lower)
        
        # Determine classifications
        requires_citizenship = citizenship_score > 0
        is_sponsorship_friendly = sponsorship_score > 0
        
        # Override logic: if explicit citizenship requirement, override sponsorship
        if requires_citizenship and any(keyword in text_lower for keyword in ['citizens only', 'us citizens only', 'no sponsorship']):
            is_sponsorship_friendly = False
        
        return {
            'requires_us_citizenship': requires_citizenship,
            'requires_security_clearance': any(keyword in text_lower for keyword in [
                'security clearance', 'government clearance', 'top secret', 'secret clearance'
            ]),
            'is_sponsorship_friendly': is_sponsorship_friendly,
            'is_f1_student_friendly': is_sponsorship_friendly and not requires_citizenship,
            'citizenship_score': citizenship_score,
            'sponsorship_score': sponsorship_score
        }
    
    def filter_citizenship_clearance(self, jobs: List[Dict], exclude_citizenship_required: bool = False) -> List[Dict]:
        """Advanced citizenship and clearance filtering with intelligent classification"""
        for job in jobs:
            # Combine title and description for analysis
            full_text = f"{job.get('title', '')} {job.get('description', '')}"
            
            # Get intelligent classifications
            classifications = self.classify_citizenship_clearance(full_text)
            
            # Update job with all classification data
            job.update(classifications)
            
            # Add UI-friendly tags
            tags = []
            if job['requires_us_citizenship']:
                tags.append('US Citizenship Required')
            if job['requires_security_clearance']:
                tags.append('Security Clearance Required')
            if job['is_sponsorship_friendly']:
                tags.append('Sponsorship Friendly')
            if job['is_f1_student_friendly']:
                tags.append('F1 Student Friendly')
            
            job['classification_tags'] = tags
        
        # Filter based on requirement
        if exclude_citizenship_required:
            # Return jobs that do NOT require citizenship
            filtered_jobs = [job for job in jobs if not job['requires_us_citizenship']]
            logger.info(f"Filtered out {len(jobs) - len(filtered_jobs)} jobs requiring citizenship")
            return filtered_jobs
        else:
            # Return all jobs with classification data
            return jobs

    def filter_f1_student_friendly(self, jobs: List[Dict], f1_student: bool = False) -> List[Dict]:
        """Filter jobs that are F1 student friendly using intelligent classification"""
        if not f1_student:
            return jobs
        
        # Use the intelligent classification already performed
        # Jobs should already have 'is_f1_student_friendly' field from filter_citizenship_clearance
        filtered_jobs = [job for job in jobs if job.get('is_f1_student_friendly', False)]
        
        logger.info(f"F1 student filter: kept {len(filtered_jobs)} out of {len(jobs)} jobs")
        return filtered_jobs

    def scrape_indeed(self, location: str = "United States", max_pages: int = 5, time_filter: str = "7", experience_level: str = "all") -> List[Dict]:
        """Scrape cybersecurity jobs from Indeed with enhanced filtering"""
        jobs = []
        base_url = "https://www.indeed.com/jobs"
        
        # Map time filters to Indeed's fromage parameter
        time_mapping = {
            "0.5": "1",  # 12 hours -> 1 day (closest option)
            "12h": "1",
            "1": "1",    # 24 hours
            "24h": "1",
            "3": "3",    # 3 days
            "3d": "3", 
            "7": "7",    # 7 days
            "7d": "7",
            "14": "14",  # 14 days
            "14d": "14",
            "30": "30",  # 30 days
            "30d": "30"
        }
        fromage = time_mapping.get(time_filter, "7")
        
        # Map experience levels to Indeed's explvl parameter
        exp_mapping = {
            "entry": "explvl%3AENTRY_LEVEL",
            "mid": "explvl%3AMID_LEVEL", 
            "senior": "explvl%3ASENIOR_LEVEL",
            "internship": "explvl%3AINTERNSHIP"
        }
        
        for page in range(max_pages):
            try:
                # Build query with experience filter
                base_query = 'cybersecurity OR "cyber security" OR "information security" OR "security engineer" OR "penetration tester"'
                if experience_level != "all" and experience_level in exp_mapping:
                    query = f"{base_query} {exp_mapping[experience_level]}"
                else:
                    query = base_query
                
                params = {
                    'q': query,
                    'l': location,
                    'start': page * 10,
                    'sort': 'date',
                    'fromage': fromage
                }
                
                response = self.session.get(base_url, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2', class_='jobTitle')
                        if not title_elem:
                            continue
                            
                        title = title_elem.get_text(strip=True)
                        
                        # Try multiple selectors for company name (Indeed changes their HTML structure)
                        company = "Unknown"
                        company_selectors = [
                            'span[data-testid="company-name"]',
                            'span.companyName',
                            '.companyName',
                            '[data-testid="company-name"]',
                            'span[title]',
                            'div[data-testid="company-name"]'
                        ]
                        
                        for selector in company_selectors:
                            company_elem = card.select_one(selector)
                            if company_elem:
                                company = company_elem.get_text(strip=True)
                                if company and company != "Unknown":
                                    break
                        
                        # Fallback: look for any span with company-like content
                        if company == "Unknown":
                            spans = card.find_all('span')
                            for span in spans:
                                text = span.get_text(strip=True)
                                if text and len(text) > 2 and len(text) < 50 and not any(char.isdigit() for char in text):
                                    company = text
                                    break
                        
                        location_elem = card.find('div', class_='companyLocation')
                        job_location = location_elem.get_text(strip=True) if location_elem else location
                        
                        # Check for sponsored job
                        sponsored = "Sponsored" in card.get_text() or "sponsored" in card.get_text()
                        
                        # Get job description link
                        link_elem = title_elem.find('a')
                        if link_elem:
                            job_url = "https://www.indeed.com" + link_elem['href']
                            
                            # Get job description
                            try:
                                desc_response = self.session.get(job_url)
                                desc_soup = BeautifulSoup(desc_response.content, 'html.parser')
                                desc_elem = desc_soup.find('div', class_='jobsearch-jobDescriptionText')
                                description = desc_elem.get_text(strip=True) if desc_elem else ""
                            except Exception:
                                description = ""
                        else:
                            description = ""
                            job_url = ""
                        
                        # Check if it's a cybersecurity job
                        if self.is_cybersecurity_job(title, description):
                            job_data = {
                                'title': title,
                                'company': company,
                                'location': job_location,
                                'description': description[:1000] + "..." if len(description) > 1000 else description,
                                'url': job_url,
                                'source': 'Indeed',
                                'scraped_at': datetime.now().isoformat(),
                                'posted_date': self._extract_date(card),
                                'sponsored': sponsored,
                                'experience_level': experience_level
                            }
                            jobs.append(job_data)
                            
                    except Exception as e:
                        logger.warning(f"Error parsing job card: {e}")
                        continue
                
                logger.info(f"Scraped page {page + 1} from Indeed")
                time.sleep(2)  # Be respectful to the server
                
            except Exception as e:
                logger.error(f"Error scraping Indeed page {page + 1}: {e}")
                continue
        
        return jobs

    def scrape_linkedin_jobs(self, location: str = "United States", max_pages: int = 3, time_filter: str = "7", experience_level: str = "all", exclude_easy_apply: bool = True) -> List[Dict]:
        """Scrape cybersecurity jobs from LinkedIn with enhanced filtering"""
        jobs = []
        
        try:
            search_terms = [
                'cybersecurity engineer',
                'security analyst',
                'information security',
                'penetration tester',
                'security consultant',
                'SOC analyst'
            ]
            
            # Map time filters to LinkedIn's f_TPR parameter
            time_mapping = {
                "0.5": "r43200",   # 12 hours
                "12h": "r43200",
                "1": "r86400",     # 24 hours
                "24h": "r86400",
                "3": "r259200",    # 3 days
                "3d": "r259200", 
                "7": "r604800",    # 7 days
                "7d": "r604800",
                "14": "r1209600",  # 14 days
                "14d": "r1209600",
                "30": "r2592000",  # 30 days
                "30d": "r2592000"
            }
            tpr_filter = time_mapping.get(time_filter, "r604800")
            
            # Map experience levels to LinkedIn's f_E parameter
            exp_mapping = {
                "entry": "2",
                "mid": "3", 
                "senior": "4",
                "internship": "1"
            }
            
            for term in search_terms:
                # Build URL with filters
                base_url = f"https://www.linkedin.com/jobs/search/?keywords={term}&location={location}&f_TPR={tpr_filter}"
                if experience_level != "all" and experience_level in exp_mapping:
                    base_url += f"&f_E={exp_mapping[experience_level]}"
                
                response = self.session.get(base_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # LinkedIn structure - this may need adjustment based on current site structure
                    job_listings = soup.find_all('div', class_='job-search-card')
                    
                    for listing in job_listings[:15]:  # Limit to avoid rate limiting
                        try:
                            title_elem = listing.find('h3', class_='base-search-card__title')
                            title = title_elem.get_text(strip=True) if title_elem else ""
                            
                            company_elem = listing.find('h4', class_='base-search-card__subtitle')
                            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                            
                            location_elem = listing.find('span', class_='job-search-card__location')
                            job_location = location_elem.get_text(strip=True) if location_elem else location
                            
                            link_elem = listing.find('a')
                            job_url = link_elem['href'] if link_elem else ""
                            
                            # Check for sponsored job
                            sponsored = "sponsored" in listing.get_text().lower()
                            
                            # Check for Easy Apply job (filter these out if exclude_easy_apply is True)
                            job_text = listing.get_text().lower()
                            is_easy_apply = any(keyword in job_text for keyword in [
                                "easy apply", "quick apply", "apply now", "one-click apply", 
                                "instant apply", "apply instantly", "fast apply", "in easy apply"
                            ])
                            
                            # Also check for Easy Apply button or icon in the HTML
                            easy_apply_buttons = listing.find_all(['button', 'span', 'div'], 
                                string=lambda text: text and any(keyword in text.lower() for keyword in [
                                    "easy apply", "quick apply", "apply now", "in easy apply"
                                ]))
                            
                            if easy_apply_buttons:
                                is_easy_apply = True
                            
                            # Additional check for LinkedIn's specific Easy Apply indicators
                            if 'linkedin' in job_url.lower():
                                # Check if the job URL contains Easy Apply indicators
                                if any(indicator in job_url.lower() for indicator in ['easy-apply', 'quick-apply']):
                                    is_easy_apply = True
                            
                            # Check for Easy Apply in button text or aria-labels
                            easy_apply_elements = listing.find_all(['button', 'span', 'div'], 
                                attrs={'aria-label': lambda x: x and any(keyword in x.lower() for keyword in [
                                    "easy apply", "quick apply", "apply now", "in easy apply"
                                ])})
                            
                            if easy_apply_elements:
                                is_easy_apply = True
                            
                            # Note: We don't skip Easy Apply jobs here anymore
                            # They will be categorized and can be filtered in the frontend
                            
                            if title and self.is_cybersecurity_job(title, ""):
                                # Determine source based on company and Easy Apply status
                                if company.lower() in ['lensa', 'dice']:
                                    source = 'Staffing'
                                    logger.info(f"👥 Staffing job detected: {title} at {company}")
                                elif is_easy_apply:
                                    source = 'Easy Apply'
                                    logger.info(f"🎯 Easy Apply job detected: {title} at {company}")
                                else:
                                    # IMPROVED Easy Apply detection
                                    is_actually_easy_apply = False
                                    
                                    # Method 1: Check the entire job listing HTML for Easy Apply indicators
                                    job_html = str(listing)
                                    easy_apply_keywords = [
                                        'easy apply', 'quick apply', 'apply now', 'one-click apply',
                                        'instant apply', 'apply instantly', 'fast apply', 'in easy apply',
                                        'easyapply', 'quickapply', 'applynow', 'easy-apply', 'quick-apply'
                                    ]
                                    
                                    # Check if any Easy Apply keywords are in the HTML
                                    for keyword in easy_apply_keywords:
                                        if keyword in job_html.lower():
                                            is_actually_easy_apply = True
                                            logger.info(f"🔍 Easy Apply detected via keyword '{keyword}': {title}")
                                            break
                                    
                                    # Method 2: Check for LinkedIn's specific Easy Apply button patterns
                                    if not is_actually_easy_apply and 'linkedin' in job_url.lower():
                                        # Look for buttons with Easy Apply text
                                        buttons = listing.find_all(['button', 'span', 'div', 'a'])
                                        for button in buttons:
                                            button_text = button.get_text().lower().strip()
                                            if any(keyword in button_text for keyword in easy_apply_keywords):
                                                is_actually_easy_apply = True
                                                logger.info(f"🔍 Easy Apply detected via button text '{button_text}': {title}")
                                                break
                                    
                                    # Method 3: Check for LinkedIn's Easy Apply button classes and attributes
                                    if not is_actually_easy_apply and 'linkedin' in job_url.lower():
                                        # Look for elements with Easy Apply related classes or attributes
                                        easy_apply_elements = listing.find_all(attrs={
                                            'class': lambda x: x and any(
                                                'easy' in str(x).lower() or 'apply' in str(x).lower() or 'quick' in str(x).lower()
                                                for x in (x if isinstance(x, list) else [x])
                                            )
                                        })
                                        
                                        if easy_apply_elements:
                                            # Double-check that these elements contain Easy Apply text
                                            for element in easy_apply_elements:
                                                element_text = element.get_text().lower()
                                                if any(keyword in element_text for keyword in easy_apply_keywords):
                                                    is_actually_easy_apply = True
                                                    logger.info(f"🔍 Easy Apply detected via LinkedIn element: {title}")
                                                    break
                                    
                                    # Method 4: Check for specific LinkedIn Easy Apply patterns in the URL
                                    if not is_actually_easy_apply and 'linkedin' in job_url.lower():
                                        url_indicators = ['easy-apply', 'quick-apply', 'easyapply', 'quickapply']
                                        if any(indicator in job_url.lower() for indicator in url_indicators):
                                            is_actually_easy_apply = True
                                            logger.info(f"🔍 Easy Apply detected via URL: {title}")
                                    
                                    # Determine final source - All LinkedIn jobs together
                                    if company.lower() in ['lensa', 'dice']:
                                        source = 'Staffing'
                                        logger.info(f"👥 Staffing job detected: {title} at {company}")
                                    else:
                                        source = 'LinkedIn'
                                        logger.info(f"💼 LinkedIn job: {title} at {company}")
                                
                                job_data = {
                                    'title': title,
                                    'company': company,
                                    'location': job_location,
                                    'description': f"Cybersecurity position at {company}. Click link for full details.",
                                    'url': job_url,
                                    'source': source,
                                    'scraped_at': datetime.now().isoformat(),
                                    'posted_date': datetime.now().isoformat(),
                                    'sponsored': sponsored,
                                    'experience_level': experience_level,
                                    'easy_apply': is_easy_apply
                                }
                                jobs.append(job_data)
                                
                        except Exception as e:
                            logger.warning(f"Error parsing LinkedIn job: {e}")
                            continue
                
                time.sleep(3)  # Longer delay for LinkedIn
                
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
        
        return jobs

    def scrape_glassdoor(self, location: str = "United States", max_pages: int = 3) -> List[Dict]:
        """Scrape cybersecurity jobs from Glassdoor"""
        jobs = []
        
        try:
            base_url = "https://www.glassdoor.com/Job/jobs.htm"
            
            for page in range(max_pages):
                params = {
                    'sc.keyword': 'cybersecurity engineer',
                    'locT': 'N',
                    'locId': '1',  # United States
                    'jobType': '',
                    'fromAge': '7',  # Last 7 days
                    'minSalary': '',
                    'includeNoSalaryJobs': 'true',
                    'radius': '100',
                    'cityId': '-1'
                }
                
                response = self.session.get(base_url, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Glassdoor structure - this may need adjustment based on current site structure
                job_cards = soup.find_all('div', {'data-test': 'jobListing'})
                
                for card in job_cards:
                    try:
                        title_elem = card.find('div', {'data-test': 'job-title'})
                        title = title_elem.get_text(strip=True) if title_elem else ""
                        
                        company_elem = card.find('div', {'data-test': 'employer-name'})
                        company = company_elem.get_text(strip=True) if company_elem else ""
                        
                        location_elem = card.find('div', {'data-test': 'job-location'})
                        job_location = location_elem.get_text(strip=True) if location_elem else location
                        
                        if title and self.is_cybersecurity_job(title, ""):
                            job_data = {
                                'title': title,
                                'company': company,
                                'location': job_location,
                                'description': f"Cybersecurity position at {company}. Click link for full details.",
                                'url': f"https://www.glassdoor.com{card.find('a')['href']}" if card.find('a') else "",
                                'source': 'Glassdoor',
                                'scraped_at': datetime.now().isoformat(),
                                'posted_date': datetime.now().isoformat()
                            }
                            jobs.append(job_data)
                            
                    except Exception as e:
                        logger.warning(f"Error parsing Glassdoor job: {e}")
                        continue
                
                logger.info(f"Scraped page {page + 1} from Glassdoor")
                time.sleep(3)
                
        except Exception as e:
            logger.error(f"Error scraping Glassdoor: {e}")
        
        return jobs

    def scrape_ziprecruiter(self, location: str = "United States", max_pages: int = 5, time_filter: str = "7", experience_level: str = "all") -> List[Dict]:
        """Scrape cybersecurity jobs from ZipRecruiter"""
        jobs = []
        base_url = "https://www.ziprecruiter.com/jobs-search"
        
        # Map time filters to ZipRecruiter parameters
        time_mapping = {
            "0.5": "1d",  # 12 hours -> 1 day (closest option)
            "12h": "1d",
            "1": "1d",    # 24 hours
            "24h": "1d",
            "3": "3d",    # 3 days
            "3d": "3d", 
            "7": "7d",    # 7 days
            "7d": "7d",
            "14": "14d",  # 14 days
            "14d": "14d",
            "30": "30d",  # 30 days
            "30d": "30d"
        }
        
        # Map experience levels to ZipRecruiter parameters
        exp_mapping = {
            "entry": "entry-level",
            "internship": "entry-level",
            "mid": "mid-level",
            "senior": "senior-level"
        }
        
        try:
            for page in range(max_pages):
                params = {
                    'search': 'cybersecurity OR "cyber security" OR "information security" OR "security engineer" OR "penetration tester"',
                    'location': location,
                    'page': page + 1,
                    'days': time_mapping.get(time_filter, "7d")
                }
                
                if experience_level != "all" and experience_level in exp_mapping:
                    params['experience'] = exp_mapping[experience_level]
                
                response = self.session.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job_content')
                
                if not job_cards:
                    break
                
                for card in job_cards:
                    try:
                        title_elem = card.find('a', class_='job_link')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        url = "https://www.ziprecruiter.com" + title_elem.get('href', '')
                        
                        # Get company
                        company_elem = card.find('a', class_='company_link')
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                        
                        # Get location
                        location_elem = card.find('div', class_='job_location')
                        location_text = location_elem.get_text(strip=True) if location_elem else location
                        
                        # Get description
                        desc_elem = card.find('div', class_='job_snippet')
                        description = desc_elem.get_text(strip=True) if desc_elem else ""
                        
                        # Get posted date
                        date_elem = card.find('div', class_='job_posted')
                        posted_date = self._extract_date(date_elem) if date_elem else datetime.now().isoformat()
                        
                        # Check if it's a cybersecurity job
                        if self.is_cybersecurity_job(title, description):
                            job_data = {
                                'title': title,
                                'company': company,
                                'location': location_text,
                                'description': description,
                                'url': url,
                                'source': 'ZipRecruiter',
                                'scraped_at': datetime.now().isoformat(),
                                'posted_date': posted_date,
                                'sponsored': False,
                                'experience_level': experience_level if experience_level != "all" else ""
                            }
                            jobs.append(job_data)
                    
                    except Exception as e:
                        logger.warning(f"Error parsing ZipRecruiter job card: {e}")
                        continue
                
                logger.info(f"Scraped page {page + 1} from ZipRecruiter")
                time.sleep(1)  # Be respectful
                
        except Exception as e:
            logger.error(f"Error scraping ZipRecruiter: {e}")
            return []
        
        return jobs

    def scrape_dice(self, location: str = "United States", max_pages: int = 5, time_filter: str = "7", experience_level: str = "all") -> List[Dict]:
        """Scrape cybersecurity jobs from Dice"""
        jobs = []
        base_url = "https://www.dice.com/jobs"
        
        # Map time filters to Dice parameters
        time_mapping = {
            "0.5": "1",  # 12 hours -> 1 day (closest option)
            "12h": "1",
            "1": "1",    # 24 hours
            "24h": "1",
            "3": "3",    # 3 days
            "3d": "3", 
            "7": "7",    # 7 days
            "7d": "7",
            "14": "14",  # 14 days
            "14d": "14",
            "30": "30",  # 30 days
            "30d": "30"
        }
        
        # Map experience levels to Dice parameters
        exp_mapping = {
            "entry": "Entry Level",
            "internship": "Entry Level",
            "mid": "Mid Level",
            "senior": "Senior Level"
        }
        
        try:
            for page in range(max_pages):
                params = {
                    'q': 'cybersecurity OR "cyber security" OR "information security" OR "security engineer" OR "penetration tester"',
                    'l': location,
                    'page': page + 1,
                    'fromage': time_mapping.get(time_filter, "7")
                }
                
                if experience_level != "all" and experience_level in exp_mapping:
                    params['experienceLevel'] = exp_mapping[experience_level]
                
                response = self.session.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='card')
                
                if not job_cards:
                    break
                
                for card in job_cards:
                    try:
                        title_elem = card.find('a', class_='card-title-link')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        
                        # Get company
                        company_elem = card.find('a', class_='card-company')
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                        
                        # Get location
                        location_elem = card.find('span', class_='jobLocation')
                        location_text = location_elem.get_text(strip=True) if location_elem else location
                        
                        # Get description
                        desc_elem = card.find('div', class_='card-description')
                        description = desc_elem.get_text(strip=True) if desc_elem else ""
                        
                        # Get posted date
                        date_elem = card.find('span', class_='posted')
                        posted_date = self._extract_date(date_elem) if date_elem else datetime.now().isoformat()
                        
                        # Check if it's a cybersecurity job
                        if self.is_cybersecurity_job(title, description):
                            job_data = {
                                'title': title,
                                'company': company,
                                'location': location_text,
                                'description': description,
                                'url': url,
                                'source': 'Dice',
                                'scraped_at': datetime.now().isoformat(),
                                'posted_date': posted_date,
                                'sponsored': False,
                                'experience_level': experience_level if experience_level != "all" else ""
                            }
                            jobs.append(job_data)
                    
                    except Exception as e:
                        logger.warning(f"Error parsing Dice job card: {e}")
                        continue
                
                logger.info(f"Scraped page {page + 1} from Dice")
                time.sleep(1)  # Be respectful
                
        except Exception as e:
            logger.error(f"Error scraping Dice: {e}")
            return []
        
        return jobs

    def scrape_wellfound(self, location: str = "United States", max_pages: int = 3, time_filter: str = "7", experience_level: str = "all") -> List[Dict]:
        """Scrape jobs from Wellfound (formerly AngelList) - startup focused"""
        jobs = []
        base_url = "https://wellfound.com/jobs"
        
        try:
            for page in range(max_pages):
                params = {
                    'search': 'cybersecurity OR "cyber security" OR "information security" OR "security engineer" OR "penetration tester"',
                    'location': location,
                    'page': page + 1,
                    'sort': 'newest'
                }
                
                response = self.session.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job-listing') or soup.find_all('div', class_='job-card') or soup.find_all('article')
                
                if not job_cards:
                    break
                
                for card in job_cards:
                    try:
                        # Try multiple selectors for title
                        title_elem = (card.find('h3') or card.find('h2') or 
                                    card.find('a', class_='job-title') or 
                                    card.find('span', class_='job-title'))
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        
                        # Try to find job URL
                        job_url_elem = card.find('a', href=True)
                        job_url = job_url_elem.get('href', '') if job_url_elem else ''
                        if job_url and not job_url.startswith('http'):
                            job_url = f"https://wellfound.com{job_url}"
                        
                        # Try multiple selectors for company
                        company_elem = (card.find('div', class_='company') or 
                                      card.find('span', class_='company-name') or
                                      card.find('h4', class_='company'))
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                        
                        # Try multiple selectors for location
                        location_elem = (card.find('div', class_='location') or 
                                       card.find('span', class_='location') or
                                       card.find('div', class_='job-location'))
                        job_location = location_elem.get_text(strip=True) if location_elem else location
                        
                        # Try to find description
                        description_elem = (card.find('div', class_='description') or 
                                          card.find('p', class_='job-description') or
                                          card.find('div', class_='job-summary'))
                        description = description_elem.get_text(strip=True) if description_elem else ""
                        
                        # Posted date
                        posted_elem = (card.find('time') or 
                                     card.find('span', class_='posted-date') or
                                     card.find('div', class_='posted'))
                        posted_date = self._extract_date(posted_elem) if posted_elem else datetime.now().isoformat()
                        
                        # Check if it's a cybersecurity job
                        if self.is_cybersecurity_job(title, description):
                            job_data = {
                                'title': title,
                                'company': company,
                                'location': job_location,
                                'description': description,
                                'url': job_url,
                                'source': 'Wellfound',
                                'scraped_at': datetime.now().isoformat(),
                                'posted_date': posted_date,
                                'sponsored': False,
                                'experience_level': experience_level if experience_level != "all" else ""
                            }
                            jobs.append(job_data)
                    
                    except Exception as e:
                        logger.warning(f"Error parsing Wellfound job card: {e}")
                        continue
                
                logger.info(f"Scraped page {page + 1} from Wellfound")
                time.sleep(2)  # Be more respectful to startup site
                
        except Exception as e:
            logger.error(f"Error scraping Wellfound: {e}")
            return []
        
        return jobs

    def scrape_google_dorks(self, location: str = "United States", max_results: int = 50, time_filter: str = "7", experience_level: str = "all", state: str = None, city: str = None) -> List[Dict]:
        """Scrape jobs using Google dorks with SERP API to find cybersecurity positions from ATS platforms and company career pages"""
        jobs = []
        
        try:
            # Check if SERP API key is available
            serp_api_key = os.getenv('SERP_API_KEY')
            if not serp_api_key:
                logger.warning("SERP_API_KEY not found. Using fallback method...")
                return self._fallback_google_search(location, max_results, time_filter, experience_level, state, city)
            
            # Check if GoogleSearch is available
            if GoogleSearch is None:
                logger.warning("GoogleSearch not available. Using fallback method...")
                return self._fallback_google_search(location, max_results, time_filter, experience_level, state, city)
            
            # Build location string
            location_str = location
            if state:
                location_str = f"{state}, {location}"
            if city:
                location_str = f"{city}, {state}, {location}"
            
            # Google dorks queries optimized for minimal SERP API calls
            dork_queries = [
                # ATS platforms with cybersecurity jobs
                f'site:*.workday.com OR site:*.greenhouse.io OR site:*.lever.co "cybersecurity engineer" OR "security analyst" OR "SOC analyst" OR "penetration tester" {location_str}',
                f'site:*.icims.com OR site:*.smartrecruiters.com OR site:*.bamboohr.com "cybersecurity engineer" OR "security analyst" OR "SOC analyst" OR "penetration tester" {location_str}',
                f'site:*.jazzhr.com OR site:*.clearcompany.com "cybersecurity engineer" OR "security analyst" OR "SOC analyst" OR "penetration tester" {location_str}',
                
                # Company career pages
                f'site:careers.* OR site:jobs.* "cybersecurity engineer" OR "security analyst" OR "SOC analyst" OR "penetration tester" {location_str}',
                f'site:*.com/careers OR site:*.com/jobs "cybersecurity engineer" OR "security analyst" OR "SOC analyst" OR "penetration tester" {location_str}',
                
                # Government and defense
                f'site:*.gov OR site:*.mil "cybersecurity engineer" OR "security analyst" OR "SOC analyst" OR "penetration tester" {location_str}',
                f'site:*.clearancejobs.com "cybersecurity engineer" OR "security analyst" OR "SOC analyst" OR "penetration tester" {location_str}',
                
                # University and startup job boards
                f'site:*.edu OR site:*.angel.co "cybersecurity engineer" OR "security analyst" OR "SOC analyst" OR "penetration tester" {location_str}',
                
                # Remote work focused
                f'site:*.remote.co OR site:*.flexjobs.com "cybersecurity engineer" OR "security analyst" OR "SOC analyst" OR "penetration tester" {location_str}'
            ]
            
            # Add experience level filters to queries
            if experience_level == "entry":
                dork_queries = [q + ' "entry level" OR "junior" OR "associate" OR "intern"' for q in dork_queries]
            elif experience_level == "internship":
                dork_queries = [q + ' "intern" OR "internship" OR "co-op"' for q in dork_queries]
            
            # Add time filters
            if time_filter == "1":
                dork_queries = [q + ' "posted today" OR "posted yesterday"' for q in dork_queries]
            elif time_filter == "3":
                dork_queries = [q + ' "posted this week"' for q in dork_queries]
            
            logger.info(f"🔍 Starting Google dorks search with SERP API for {location_str}...")
            
            # Process each dork query (limit to 5 queries to minimize API usage)
            for i, query in enumerate(dork_queries[:5]):
                try:
                    logger.info(f"🔍 Processing dork query {i+1}/5: {query[:80]}...")
                    
                    # Use SERP API for Google search
                    search_params = {
                        "q": query,
                        "api_key": serp_api_key,
                        "num": 10,  # Limit results per query
                        "safe": "active"
                    }
                    
                    search = GoogleSearch(search_params)
                    results = search.get_dict()
                    
                    # Extract organic results
                    organic_results = results.get("organic_results", [])
                    
                    for result in organic_results[:5]:  # Limit to top 5 results per query
                        try:
                            title = result.get("title", "")
                            link = result.get("link", "")
                            snippet = result.get("snippet", "")
                            
                            # Check if it's a cybersecurity job
                            if self.is_cybersecurity_job(title, snippet):
                                # Try to extract more details from the job page
                                job_data = self._extract_job_details_from_url(link, title, snippet, location_str)
                                if job_data:
                                    jobs.append(job_data)
                                    logger.info(f"✅ Found job via dorks: {title}")
                        except Exception as e:
                            logger.warning(f"Error processing search result: {e}")
                            continue
                    
                    # Be respectful with rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Error processing dork query: {e}")
                    continue
            
            logger.info(f"✅ Google dorks search completed. Found {len(jobs)} jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"Error in Google dorks search: {e}")
            return self._fallback_google_search(location, max_results, time_filter, experience_level, state, city)

    def _fallback_google_search(self, location: str, max_results: int, time_filter: str, experience_level: str, state: str, city: str) -> List[Dict]:
        """Fallback method when SERP API is not available"""
        logger.info("Using fallback Google search method...")
        # This would implement a basic web scraping approach
        # For now, return empty list to avoid errors
        return []

    def _extract_job_details_from_url(self, url: str, title: str, description: str, location: str) -> Dict:
        """Extract detailed job information from a job posting URL"""
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to extract company name from various sources
            company = "Unknown"
            company_selectors = [
                'h1.company-name', '.company-name', '.employer-name', '.company',
                'h2.company', '.job-company', '.company-title', '.employer',
                '.job-header-company', '.company-info', '.employer-info'
            ]
            
            for selector in company_selectors:
                company_elem = soup.select_one(selector)
                if company_elem:
                    company = company_elem.get_text(strip=True)
                    break
            
            # If no company found, try to extract from URL
            if company == "Unknown":
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc
                    if domain:
                        company = domain.replace('www.', '').split('.')[0].title()
                except Exception:
                    pass
            
            # Try to extract job location
            job_location = location
            location_selectors = [
                '.location', '.job-location', '.workplace', '.place',
                '.job-place', '.location-info', '.work-location',
                '.job-details-location', '.position-location'
            ]
            
            for selector in location_selectors:
                location_elem = soup.select_one(selector)
                if location_elem:
                    job_location = location_elem.get_text(strip=True)
                    break
            
            # Try to extract full job description
            full_description = description
            desc_selectors = [
                '.job-description', '.description', '.job-content', '.job-details',
                '.content', '.job-summary', '.requirements', '.responsibilities',
                '.job-body', '.position-description', '.role-description'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    full_description = desc_elem.get_text(strip=True)
                    break
            
            # Check if it's Easy Apply
            is_easy_apply = False
            easy_apply_keywords = ['easy apply', 'quick apply', 'apply now', 'one-click apply', 'instant apply']
            page_text = soup.get_text().lower()
            for keyword in easy_apply_keywords:
                if keyword in page_text:
                    is_easy_apply = True
                    break
            
            # Determine source based on URL
            source = "Google Dorks"
            if 'workday.com' in url:
                source = "Workday ATS"
            elif 'greenhouse.io' in url:
                source = "Greenhouse ATS"
            elif 'lever.co' in url:
                source = "Lever ATS"
            elif 'icims.com' in url:
                source = "iCIMS ATS"
            elif 'smartrecruiters.com' in url:
                source = "SmartRecruiters ATS"
            elif 'bamboohr.com' in url:
                source = "BambooHR ATS"
            elif 'jazzhr.com' in url:
                source = "JazzHR ATS"
            elif 'careers.' in url or 'jobs.' in url:
                source = "Company Career Page"
            elif '.gov' in url or '.mil' in url:
                source = "Government/Defense"
            elif '.edu' in url:
                source = "University Job Board"
            elif 'clearancejobs.com' in url:
                source = "ClearanceJobs"
            elif 'angel.co' in url:
                source = "AngelList"
            elif 'remote.co' in url or 'flexjobs.com' in url:
                source = "Remote Job Board"
            
            job_data = {
                'title': title,
                'company': company,
                'location': job_location,
                'description': full_description,
                'url': url,
                'source': source,
                'scraped_at': datetime.now().isoformat(),
                'posted_date': datetime.now().isoformat(),
                'sponsored': False,
                'experience_level': "all",
                'easy_apply': is_easy_apply
            }
            
            return job_data
            
        except Exception as e:
            logger.warning(f"Error extracting job details from {url}: {e}")
            return None

    def _extract_date(self, job_card) -> str:
        """Extract posted date from job card"""
        try:
            date_elem = job_card.find('span', class_='date')
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                # Parse relative dates like "2 days ago"
                if 'day' in date_text:
                    days = int(re.search(r'(\d+)', date_text).group(1))
                    return (datetime.now() - timedelta(days=days)).isoformat()
                elif 'hour' in date_text:
                    return datetime.now().isoformat()
            return datetime.now().isoformat()
        except Exception:
            return datetime.now().isoformat()

    def scrape_all_sources(self, location: str = "United States", time_filter: str = "7", experience_level: str = "all", sources: List[str] = None, exclude_citizenship_required: bool = False, f1_student: bool = False, exclude_easy_apply: bool = True, keywords: str = "") -> List[Dict]:
        """Scrape jobs from all sources with advanced filtering and intelligent classification"""
        all_jobs = []
        
        # Default to all sources if none specified
        if sources is None:
            sources = ['Indeed', 'LinkedIn', 'Glassdoor', 'ZipRecruiter', 'Dice', 'Wellfound', 'Google Dorks']
        
        logger.info(f"Starting job scraping from {', '.join(sources)}...")
        logger.info(f"Filters: Easy Apply excluded={exclude_easy_apply}, Exclude Citizenship Required={exclude_citizenship_required}, F1 Student={f1_student}")
        
        # Scrape from Indeed
        if 'Indeed' in sources:
            logger.info("🔍 Scraping Indeed...")
            indeed_jobs = self.scrape_indeed(location, time_filter=time_filter, experience_level=experience_level)
            logger.info(f"✅ Found {len(indeed_jobs)} jobs from Indeed")
            all_jobs.extend(indeed_jobs)
        
        # Scrape from LinkedIn
        if 'LinkedIn' in sources:
            logger.info("🔍 Scraping LinkedIn...")
            linkedin_jobs = self.scrape_linkedin_jobs(location, time_filter=time_filter, experience_level=experience_level, exclude_easy_apply=exclude_easy_apply)
            logger.info(f"✅ Found {len(linkedin_jobs)} jobs from LinkedIn")
            all_jobs.extend(linkedin_jobs)
        
        # Scrape from Glassdoor
        if 'Glassdoor' in sources:
            logger.info("🔍 Scraping Glassdoor...")
            glassdoor_jobs = self.scrape_glassdoor(location)
            logger.info(f"✅ Found {len(glassdoor_jobs)} jobs from Glassdoor")
            all_jobs.extend(glassdoor_jobs)
        
        # Scrape from ZipRecruiter
        if 'ZipRecruiter' in sources:
            logger.info("🔍 Scraping ZipRecruiter...")
            ziprecruiter_jobs = self.scrape_ziprecruiter(location, time_filter=time_filter, experience_level=experience_level)
            logger.info(f"✅ Found {len(ziprecruiter_jobs)} jobs from ZipRecruiter")
            all_jobs.extend(ziprecruiter_jobs)
        
        # Scrape from Dice
        if 'Dice' in sources:
            logger.info("🔍 Scraping Dice...")
            dice_jobs = self.scrape_dice(location, time_filter=time_filter, experience_level=experience_level)
            logger.info(f"✅ Found {len(dice_jobs)} jobs from Dice")
            all_jobs.extend(dice_jobs)
        
        # Scrape from Wellfound
        if 'Wellfound' in sources:
            logger.info("🔍 Scraping Wellfound...")
            wellfound_jobs = self.scrape_wellfound(location, time_filter=time_filter, experience_level=experience_level)
            logger.info(f"✅ Found {len(wellfound_jobs)} jobs from Wellfound")
            all_jobs.extend(wellfound_jobs)
        
        # Scrape from Google Dorks (ATS platforms and company career pages)
        if 'Google Dorks' in sources:
            logger.info("🔍 Scraping Google Dorks (ATS platforms)...")
            dorks_jobs = self.scrape_google_dorks(location, time_filter=time_filter, experience_level=experience_level)
            logger.info(f"✅ Found {len(dorks_jobs)} jobs from Google Dorks")
            all_jobs.extend(dorks_jobs)
        
        # Advanced deduplication with canonicalization and fuzzy matching
        logger.info(f"Total jobs scraped before deduplication: {len(all_jobs)}")
        all_jobs = self.remove_duplicates(all_jobs)
        logger.info(f"Total jobs after deduplication: {len(all_jobs)}")
        
        # Apply intelligent citizenship and clearance classification
        all_jobs = self.filter_citizenship_clearance(all_jobs, exclude_citizenship_required=exclude_citizenship_required)
        
        # Apply F1 student filtering if requested
        if f1_student:
            all_jobs = self.filter_f1_student_friendly(all_jobs, f1_student=True)
            logger.info(f"Total jobs after F1 student filter: {len(all_jobs)}")
        
        logger.info(f"Final total jobs: {len(all_jobs)}")
        return all_jobs

    def save_to_csv(self, jobs: List[Dict], filename: str = None) -> str:
        """Save jobs to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cybersecurity_jobs_{timestamp}.csv"
        
        df = pd.DataFrame(jobs)
        filepath = f"/Users/siddh/Masters/Job Scraper/{filename}"
        df.to_csv(filepath, index=False)
        
        logger.info(f"Jobs saved to {filepath}")
        return filepath

    def save_to_json(self, jobs: List[Dict], filename: str = None) -> str:
        """Save jobs to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cybersecurity_jobs_{timestamp}.json"
        
        filepath = f"/Users/siddh/Masters/Job Scraper/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Jobs saved to {filepath}")
        return filepath

    def generate_pdf_report(self, jobs: List[Dict], filename: str = None) -> str:
        """Generate a comprehensive PDF report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cybersecurity_jobs_report_{timestamp}.pdf"
        
        filepath = f"/Users/siddh/Masters/Job Scraper/{filename}"
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Content
        story = []
        
        # Title
        story.append(Paragraph("Cybersecurity Jobs Report", title_style))
        story.append(Spacer(1, 12))
        
        # Summary
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Paragraph(f"Total Jobs Found: {len(jobs)}", styles['Normal']))
        
        # Source breakdown
        sources = {}
        for job in jobs:
            source = job['source']
            sources[source] = sources.get(source, 0) + 1
        
        story.append(Paragraph("Jobs by Source:", styles['Normal']))
        for source, count in sources.items():
            story.append(Paragraph(f"• {source}: {count} jobs", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Top companies
        companies = {}
        for job in jobs:
            company = job['company']
            companies[company] = companies.get(company, 0) + 1
        
        top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]
        
        story.append(Paragraph("Top Companies Hiring:", heading_style))
        for company, count in top_companies:
            story.append(Paragraph(f"• {company}: {count} positions", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Job listings
        story.append(Paragraph("Job Listings", heading_style))
        
        # Create table for job listings with enhanced information
        table_data = [['Title', 'Company', 'Location', 'Source', 'Sponsored']]
        
        for job in jobs[:50]:  # Limit to first 50 jobs for readability
            sponsored_text = "Yes" if job.get('sponsored', False) else "No"
            table_data.append([
                job['title'][:45] + "..." if len(job['title']) > 45 else job['title'],
                job['company'][:25] + "..." if len(job['company']) > 25 else job['company'],
                job['location'][:20] + "..." if len(job['location']) > 20 else job['location'],
                job['source'],
                sponsored_text
            ])
        
        job_table = Table(table_data)
        job_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(job_table)
        
        # Add job links section
        story.append(Spacer(1, 20))
        story.append(Paragraph("Job Application Links", heading_style))
        
        for i, job in enumerate(jobs[:20], 1):  # Show first 20 job links
            if job.get('url'):
                link_text = f"{i}. {job['title']} at {job['company']}"
                story.append(Paragraph(link_text, styles['Normal']))
                story.append(Paragraph(f"   Link: {job['url']}", styles['Normal']))
                story.append(Spacer(1, 8))
        
        if len(jobs) > 20:
            story.append(Paragraph(f"... and {len(jobs) - 20} more jobs. Check the CSV/JSON files for complete links.", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"PDF report saved to {filepath}")
        return filepath

    def create_visualization(self, jobs: List[Dict]) -> str:
        """Create visualization charts for the jobs data"""
        try:
            if not jobs:
                return None
            
            # Prepare data
            sources = {}
            locations = {}
            companies = {}
            
            for job in jobs:
                # Source data
                source = job.get('source', 'Unknown')
                sources[source] = sources.get(source, 0) + 1
                
                # Location data
                location = job.get('location', 'Unknown')
                # Extract state/city from location
                if ',' in location:
                    state = location.split(',')[-1].strip()
                    locations[state] = locations.get(state, 0) + 1
                else:
                    locations[location] = locations.get(location, 0) + 1
                
                # Company data
                company = job.get('company', 'Unknown')
                companies[company] = companies.get(company, 0) + 1
            
            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Cybersecurity Jobs Analysis', fontsize=16, fontweight='bold')
            
            # Source distribution
            if sources:
                ax1.pie(sources.values(), labels=sources.keys(), autopct='%1.1f%%', startangle=90)
                ax1.set_title('Jobs by Source')
            else:
                ax1.text(0.5, 0.5, 'No source data', ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('Jobs by Source')
            
            # Top locations
            top_locations = dict(sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10])
            if top_locations:
                ax2.barh(list(top_locations.keys()), list(top_locations.values()))
                ax2.set_title('Top Locations')
                ax2.set_xlabel('Number of Jobs')
            else:
                ax2.text(0.5, 0.5, 'No location data', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Top Locations')
            
            # Top companies
            top_companies = dict(sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10])
            if top_companies:
                ax3.bar(range(len(top_companies)), list(top_companies.values()))
                ax3.set_xticks(range(len(top_companies)))
                ax3.set_xticklabels(list(top_companies.keys()), rotation=45, ha='right')
                ax3.set_title('Top Companies')
                ax3.set_ylabel('Number of Jobs')
            else:
                ax3.text(0.5, 0.5, 'No company data', ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('Top Companies')
            
            # Jobs over time (simulated)
            ax4.plot(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], [5, 8, 12, 15, 10])
            ax4.set_title('Job Postings Trend')
            ax4.set_ylabel('Number of Jobs')
            
            plt.tight_layout()
            
            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_filename = f"/Users/siddh/Masters/Job Scraper/jobs_analysis_{timestamp}.png"
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Visualization saved to {plot_filename}")
            return plot_filename
            
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return None

if __name__ == "__main__":
    scraper = CyberSecurityJobScraper()
    
    # Scrape jobs from all sources
    jobs = scraper.scrape_all_sources("United States")
    
    if jobs:
        # Save to CSV and JSON
        csv_file = scraper.save_to_csv(jobs)
        json_file = scraper.save_to_json(jobs)
        
        # Generate PDF report
        pdf_file = scraper.generate_pdf_report(jobs)
        
        # Create visualization
        viz_file = scraper.create_visualization(jobs)
        
        print(f"\n🎉 Scraping completed!")
        print(f"Found {len(jobs)} cybersecurity jobs")
        print(f"📄 CSV: {csv_file}")
        print(f"📄 JSON: {json_file}")
        print(f"📄 PDF Report: {pdf_file}")
        if viz_file:
            print(f"📊 Visualization: {viz_file}")
        else:
            print("📊 Visualization: Failed to create (running in background thread)")
        
        # Display summary
        sources = {}
        for job in jobs:
            source = job['source']
            sources[source] = sources.get(source, 0) + 1
        
        print("\nJobs by source:")
        for source, count in sources.items():
            print(f"  {source}: {count} jobs")
    else:
        print("No jobs found. Try adjusting the search parameters.")