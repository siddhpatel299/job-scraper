"""
Unified Job Scraper Architecture
Eliminates code duplication between CyberSecurityJobScraper and SoftwareEngineeringJobScraper
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from datetime import datetime, timedelta
from fake_useragent import UserAgent
import re
import random
from typing import List, Dict, Optional, Set, Callable
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from rapidfuzz import fuzz
from urllib.parse import urlparse, parse_qs

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JobCategory(Enum):
    CYBERSECURITY = "cybersecurity"
    SOFTWARE_ENGINEERING = "software_engineering"


class JobSource(Enum):
    INDEED = "Indeed"
    LINKEDIN = "LinkedIn"
    GLASSDOOR = "Glassdoor"
    ZIPRECRUITER = "ZipRecruiter"
    DICE = "Dice"
    WELLFOUND = "Wellfound"
    GOOGLE_DORKS = "Google Dorks"


@dataclass
class JobKeywords:
    """Job category-specific keywords and titles"""
    keywords: Set[str] = field(default_factory=set)
    job_titles: Set[str] = field(default_factory=set)
    exclusions: Set[str] = field(default_factory=set)


@dataclass
class ScrapingConfig:
    """Configuration for scraping parameters"""
    max_pages: int = 3
    delay_range: tuple = (1, 3)
    timeout: int = 10
    max_retries: int = 3
    user_agents: List[str] = field(default_factory=list)


@dataclass
class JobListing:
    """Standardized job listing structure"""
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    posted_date: str
    experience_level: Optional[str] = None
    salary_range: Optional[str] = None
    classification_tags: List[str] = field(default_factory=list)
    sponsored: bool = False
    remote_friendly: bool = False
    visa_sponsorship: bool = False
    security_clearance_required: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for compatibility"""
        return {
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'url': self.url,
            'source': self.source,
            'posted_date': self.posted_date,
            'experience_level': self.experience_level,
            'salary_range': self.salary_range,
            'classification_tags': self.classification_tags,
            'sponsored': self.sponsored,
            'remote_friendly': self.remote_friendly,
            'visa_sponsorship': self.visa_sponsorship,
            'security_clearance_required': self.security_clearance_required,
        }


class JobCategoryConfig:
    """Configuration for different job categories"""
    
    @staticmethod
    def get_cybersecurity_config() -> JobKeywords:
        keywords = {
            'cybersecurity', 'cyber security', 'information security', 'infosec',
            'security engineer', 'security analyst', 'penetration tester', 'pen tester',
            'security consultant', 'SOC analyst', 'incident response', 'threat hunter',
            'vulnerability assessment', 'risk assessment', 'compliance', 'audit',
            'firewall', 'intrusion detection', 'SIEM', 'threat intelligence',
            'malware analysis', 'forensics', 'cryptography', 'identity management',
            'access control', 'security architecture', 'security operations',
            'threat modeling', 'security testing', 'ethical hacking',
            'security clearance', 'CISSP', 'CISM', 'CISA', 'CEH', 'GSEC',
            # Junior-level keywords
            'junior security', 'entry level security', 'associate security', 'trainee security',
            'security trainee', 'security intern', 'cybersecurity intern', 'security apprentice',
            'level 1 security', 'l1 security', 'security associate', 'junior analyst',
            'entry level analyst', 'associate analyst', 'security coordinator', 'security assistant'
        }
        
        job_titles = {
            'security engineer', 'security analyst', 'cybersecurity engineer',
            'information security analyst', 'security consultant', 'penetration tester',
            'security architect', 'SOC analyst', 'SOC engineer', 'SOC manager',
            'incident response analyst', 'threat intelligence analyst', 'malware analyst',
            'security operations analyst', 'vulnerability analyst', 'compliance analyst',
            'risk analyst', 'security auditor', 'forensics analyst', 'threat hunter',
            'chief information security officer', 'security administrator',
            'security specialist', 'security coordinator', 'risk analyst',
            'security auditor', 'security technician', 'cybersecurity specialist',
            # Junior variations
            'junior security engineer', 'junior security analyst', 'junior SOC analyst',
            'entry level security analyst', 'associate security engineer',
        }
        
        return JobKeywords(keywords=keywords, job_titles=job_titles)
    
    @staticmethod
    def get_software_engineering_config() -> JobKeywords:
        keywords = {
            'software engineer', 'software developer', 'programmer', 'developer',
            'full stack', 'frontend', 'backend', 'web developer', 'mobile developer',
            'python', 'javascript', 'java', 'react', 'angular', 'vue', 'node.js',
            'machine learning', 'artificial intelligence', 'data science', 'data engineer',
            'devops', 'cloud engineer', 'aws', 'azure', 'kubernetes', 'docker',
            'microservices', 'api', 'rest', 'graphql', 'database', 'sql', 'nosql',
            'agile', 'scrum', 'git', 'ci/cd', 'jenkins', 'terraform', 'ansible',
            'system design', 'architecture', 'scalability', 'performance',
        }
        
        job_titles = {
            'software engineer', 'software developer', 'senior software engineer',
            'lead software engineer', 'principal software engineer', 'staff software engineer',
            'distinguished software engineer', 'software architect', 'tech lead',
            'full stack developer', 'frontend developer', 'backend developer',
            'web developer', 'mobile developer', 'ios developer', 'android developer',
            'data engineer', 'ml engineer', 'devops engineer', 'cloud engineer',
            'junior software engineer', 'entry level software engineer',
        }
        
        return JobKeywords(keywords=keywords, job_titles=job_titles)


class BaseJobScraper(ABC):
    """Abstract base class for job scrapers"""
    
    def __init__(self, category: JobCategory, config: ScrapingConfig = None):
        self.category = category
        self.config = config or ScrapingConfig()
        self.ua = UserAgent()
        self.session = requests.Session()
        self._setup_session()
        
        # Get category-specific configuration
        if category == JobCategory.CYBERSECURITY:
            self.job_config = JobCategoryConfig.get_cybersecurity_config()
        elif category == JobCategory.SOFTWARE_ENGINEERING:
            self.job_config = JobCategoryConfig.get_software_engineering_config()
        else:
            raise ValueError(f"Unsupported job category: {category}")
    
    def _setup_session(self):
        """Setup HTTP session with headers and configuration"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def is_relevant_job(self, title: str, description: str, keywords: str = "") -> bool:
        """Check if a job posting is relevant to the category"""
        text = (title + ' ' + description + ' ' + keywords).lower()
        
        # Check for category-specific keywords
        for keyword in self.job_config.keywords:
            if keyword.lower() in text:
                return True
        
        # Check for category-specific job titles
        for job_title in self.job_config.job_titles:
            if job_title.lower() in text:
                return True
        
        return False
    
    def classify_job(self, job_data: Dict) -> JobListing:
        """Classify and enhance job data"""
        title = job_data.get('title', '')
        description = job_data.get('description', '')
        location = job_data.get('location', '')
        
        # Create JobListing object
        job = JobListing(
            title=title,
            company=job_data.get('company', ''),
            location=location,
            description=description,
            url=job_data.get('url', ''),
            source=job_data.get('source', ''),
            posted_date=job_data.get('posted_date', ''),
            experience_level=job_data.get('experience_level'),
            salary_range=job_data.get('salary_range'),
            sponsored=job_data.get('sponsored', False),
        )
        
        # Classify job characteristics
        text = (title + ' ' + description + ' ' + location).lower()
        
        # Remote work detection
        remote_keywords = ['remote', 'work from home', 'telecommute', 'distributed', 'anywhere']
        job.remote_friendly = any(keyword in text for keyword in remote_keywords)
        
        # Visa sponsorship detection
        visa_keywords = ['visa sponsorship', 'h1b', 'sponsor visa', 'work authorization']
        job.visa_sponsorship = any(keyword in text for keyword in visa_keywords)
        
        # Security clearance detection (mainly for cybersecurity)
        clearance_keywords = ['security clearance', 'top secret', 'secret clearance', 'ts/sci']
        job.security_clearance_required = any(keyword in text for keyword in clearance_keywords)
        
        # Experience level detection
        if not job.experience_level:
            if any(keyword in text for keyword in ['senior', 'sr.', 'lead', 'principal', 'staff']):
                job.experience_level = 'senior'
            elif any(keyword in text for keyword in ['junior', 'jr.', 'entry', 'associate', 'intern']):
                job.experience_level = 'entry'
            else:
                job.experience_level = 'mid'
        
        # Classification tags
        tags = []
        
        if job.remote_friendly:
            tags.append('Remote Friendly')
        
        if job.visa_sponsorship:
            tags.append('Visa Sponsorship Available')
        
        if job.security_clearance_required:
            tags.append('Security Clearance Required')
        else:
            tags.append('No Security Clearance Required')
        
        # F1 student friendly detection
        citizenship_required = any(keyword in text for keyword in [
            'us citizen', 'citizenship required', 'must be citizen',
            'security clearance', 'clearance required'
        ])
        
        if not citizenship_required and not job.security_clearance_required:
            tags.append('F1 Student Friendly')
        
        job.classification_tags = tags
        
        return job
    
    @abstractmethod
    def scrape_source(self, source: JobSource, **kwargs) -> List[JobListing]:
        """Scrape jobs from a specific source"""
        pass
    
    def scrape_all_sources(self, 
                          location: str = "United States",
                          time_filter: str = "7d",
                          experience_level: str = "all",
                          sources: List[str] = None,
                          exclude_citizenship_required: bool = False,
                          f1_student: bool = False,
                          exclude_easy_apply: bool = True,
                          keywords: str = "") -> List[Dict]:
        """Scrape jobs from all specified sources"""
        
        if sources is None:
            sources = [source.value for source in JobSource if source != JobSource.GOOGLE_DORKS]
        
        all_jobs = []
        
        for source_name in sources:
            try:
                source = JobSource(source_name)
                logger.info(f"Scraping {source.value}...")
                
                jobs = self.scrape_source(
                    source,
                    location=location,
                    time_filter=time_filter,
                    experience_level=experience_level,
                    keywords=keywords
                )
                
                all_jobs.extend([job.to_dict() for job in jobs])
                logger.info(f"Found {len(jobs)} jobs from {source.value}")
                
                # Respectful delay between sources
                time.sleep(random.uniform(*self.config.delay_range))
                
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {str(e)}")
                continue
        
        # Apply filters
        if exclude_citizenship_required or f1_student:
            all_jobs = [job for job in all_jobs if 'F1 Student Friendly' in job.get('classification_tags', [])]
        
        # Remove duplicates
        all_jobs = self.remove_duplicates(all_jobs)
        
        logger.info(f"Total unique jobs found: {len(all_jobs)}")
        return all_jobs
    
    def remove_duplicates(self, jobs: List[Dict], similarity_threshold: int = 85) -> List[Dict]:
        """Remove duplicate job listings based on similarity"""
        if not jobs:
            return jobs
        
        unique_jobs = []
        seen_jobs = []
        
        for job in jobs:
            is_duplicate = False
            job_signature = f"{job['title']} {job['company']} {job['location']}"
            
            for seen_signature in seen_jobs:
                similarity = fuzz.ratio(job_signature.lower(), seen_signature.lower())
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_jobs.append(job)
                seen_jobs.append(job_signature)
        
        logger.info(f"Removed {len(jobs) - len(unique_jobs)} duplicate jobs")
        return unique_jobs
    
    def save_to_csv(self, jobs: List[Dict], filename: str = None) -> str:
        """Save jobs to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = self.category.value
            filename = f"{prefix}_jobs_{timestamp}.csv"
        
        df = pd.DataFrame(jobs)
        filepath = f"/Users/siddh/Masters/Job Scraper/{filename}"
        df.to_csv(filepath, index=False)
        logger.info(f"Saved {len(jobs)} jobs to {filename}")
        return filepath
    
    def save_to_json(self, jobs: List[Dict], filename: str = None) -> str:
        """Save jobs to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = self.category.value
            filename = f"{prefix}_jobs_{timestamp}.json"
        
        filepath = f"/Users/siddh/Masters/Job Scraper/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(jobs)} jobs to {filename}")
        return filepath
    
    def generate_pdf_report(self, jobs: List[Dict], filename: str = None) -> str:
        """Generate PDF report of jobs"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = self.category.value
            filename = f"{prefix}_jobs_report_{timestamp}.pdf"
        
        filepath = f"/Users/siddh/Masters/Job Scraper/{filename}"
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_text = f"{self.category.value.replace('_', ' ').title()} Jobs Report"
        story.append(Paragraph(title_text, styles['Title']))
        story.append(Spacer(1, 12))
        
        # Summary
        summary_text = f"Total Jobs Found: {len(jobs)}<br/>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Jobs table
        if jobs:
            data = [['Title', 'Company', 'Location', 'Source']]
            for job in jobs[:50]:  # Limit to first 50 jobs
                data.append([
                    job.get('title', '')[:40],
                    job.get('company', '')[:30],
                    job.get('location', '')[:30],
                    job.get('source', '')
                ])
            
            table = Table(data, colWidths=[2.5*inch, 2*inch, 2*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        
        doc.build(story)
        logger.info(f"Generated PDF report: {filename}")
        return filepath


class UnifiedJobScraper(BaseJobScraper):
    """Unified job scraper implementation"""
    
    def scrape_source(self, source: JobSource, **kwargs) -> List[JobListing]:
        """Scrape jobs from a specific source"""
        if source == JobSource.INDEED:
            return self._scrape_indeed(**kwargs)
        elif source == JobSource.LINKEDIN:
            return self._scrape_linkedin(**kwargs)
        elif source == JobSource.GLASSDOOR:
            return self._scrape_glassdoor(**kwargs)
        # Add other sources as needed
        else:
            logger.warning(f"Source {source.value} not implemented yet")
            return []
    
    def _scrape_indeed(self, location: str = "United States", 
                      time_filter: str = "7d", 
                      keywords: str = "",
                      max_pages: int = 3) -> List[JobListing]:
        """Scrape Indeed jobs"""
        jobs = []
        base_url = "https://www.indeed.com/jobs"
        
        # Build query based on category
        if self.category == JobCategory.CYBERSECURITY:
            base_query = 'cybersecurity OR "information security" OR "security analyst" OR "security engineer"'
        else:  # SOFTWARE_ENGINEERING
            base_query = 'software engineer OR "software developer" OR "full stack" OR "frontend" OR "backend"'
        
        if keywords:
            base_query += f' OR {keywords}'
        
        for page in range(max_pages):
            try:
                params = {
                    'q': base_query,
                    'l': location,
                    'start': page * 10,
                    'fromage': time_filter.replace('d', '') if 'd' in time_filter else '7'
                }
                
                response = self.session.get(base_url, params=params, timeout=self.config.timeout)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards:
                    try:
                        # Extract job data
                        title_elem = card.find('h2', class_='jobTitle')
                        title = title_elem.get_text(strip=True) if title_elem else ""
                        
                        company_elem = card.find('span', class_='companyName')
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                        
                        location_elem = card.find('div', class_='companyLocation')
                        job_location = location_elem.get_text(strip=True) if location_elem else location
                        
                        summary_elem = card.find('div', class_='summary')
                        description = summary_elem.get_text(strip=True) if summary_elem else ""
                        
                        link_elem = title_elem.find('a') if title_elem else None
                        job_url = f"https://www.indeed.com{link_elem['href']}" if link_elem and link_elem.get('href') else ""
                        
                        # Check if relevant
                        if self.is_relevant_job(title, description, keywords):
                            job_data = {
                                'title': title,
                                'company': company,
                                'location': job_location,
                                'description': description,
                                'url': job_url,
                                'source': JobSource.INDEED.value,
                                'posted_date': datetime.now().isoformat(),
                            }
                            
                            job = self.classify_job(job_data)
                            jobs.append(job)
                    
                    except Exception as e:
                        logger.error(f"Error parsing job card: {str(e)}")
                        continue
                
                # Respectful delay
                time.sleep(random.uniform(*self.config.delay_range))
                
            except Exception as e:
                logger.error(f"Error scraping Indeed page {page}: {str(e)}")
                continue
        
        return jobs
    
    def _scrape_linkedin(self, **kwargs) -> List[JobListing]:
        """Scrape LinkedIn jobs - placeholder implementation"""
        logger.info("LinkedIn scraping not fully implemented in unified scraper")
        return []
    
    def _scrape_glassdoor(self, **kwargs) -> List[JobListing]:
        """Scrape Glassdoor jobs - placeholder implementation"""
        logger.info("Glassdoor scraping not fully implemented in unified scraper")
        return []


# Convenience classes for backward compatibility
class CyberSecurityJobScraper(UnifiedJobScraper):
    """Cybersecurity job scraper - now uses unified architecture"""
    
    def __init__(self):
        super().__init__(JobCategory.CYBERSECURITY)


class SoftwareEngineeringJobScraper(UnifiedJobScraper):
    """Software engineering job scraper - now uses unified architecture"""
    
    def __init__(self):
        super().__init__(JobCategory.SOFTWARE_ENGINEERING)


# Example usage
if __name__ == "__main__":
    # Test cybersecurity scraper
    cyber_scraper = CyberSecurityJobScraper()
    cyber_jobs = cyber_scraper.scrape_all_sources(
        location="San Francisco",
        sources=["Indeed"],
        max_pages=1
    )
    print(f"Found {len(cyber_jobs)} cybersecurity jobs")
    
    # Test software engineering scraper
    software_scraper = SoftwareEngineeringJobScraper()
    software_jobs = software_scraper.scrape_all_sources(
        location="San Francisco", 
        sources=["Indeed"],
        max_pages=1
    )
    print(f"Found {len(software_jobs)} software engineering jobs")
