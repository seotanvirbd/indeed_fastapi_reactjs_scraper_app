# backend/app/scraper.py
from seleniumbase import SB
import pandas as pd
import json
import time
import random
import sys
import logging
from datetime import datetime
from itertools import cycle
from typing import List, Dict, Optional

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rotate realistic user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]

class IndeedScraper:
    def __init__(self):
        logger.info("🤖 Initializing IndeedScraper with CDP mode")
        self.ua_cycle = cycle(USER_AGENTS)
        self.jobs_data = []
        self.scraping_stats = {
            'start_time': None,
            'end_time': None,
            'pages_attempted': 0,
            'pages_completed': 0,
            'jobs_found': 0,
            'errors_encountered': 0
        }
        
    def human_sleep(self, min_s=0.6, max_s=2.0):
        """Human-like sleep delays with logging"""
        sleep_time = random.uniform(min_s, max_s)
        logger.debug(f"⏳ Sleeping for {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
    
    def try_select_all_with_retries(self, sb, selector: str, retries: int = 3, backoff: float = 1.2) -> Optional[List]:
        """
        Retry sb.cdp.select_all with small backoff/refresh to handle timing issues
        """
        logger.debug(f"🔍 Attempting to select elements: {selector}")
        
        for attempt in range(1, retries + 1):
            try:
                logger.debug(f"🔄 Select attempt {attempt}/{retries}")
                elements = sb.cdp.select_all(selector)
                
                if elements:
                    logger.info(f"✅ Found {len(elements)} elements with selector: {selector}")
                    return elements
                else:
                    logger.warning(f"⚠️ No elements found with selector: {selector}")
                    
            except Exception as e:
                logger.warning(f"❌ Select attempt {attempt} failed: {str(e)}")
                self.scraping_stats['errors_encountered'] += 1
                
                if attempt < retries:
                    logger.info(f"🔄 Retrying in {backoff * attempt} seconds...")
                    self.human_sleep(1.0, 2.5)
                    
                    try:
                        logger.debug("📜 Scrolling to body")
                        sb.cdp.scroll_into_view("body")
                    except Exception as scroll_error:
                        logger.debug(f"Scroll error (non-critical): {scroll_error}")
                    
                    # Light refresh - avoid heavy reloads
                    try:
                        current_url = sb.get_current_url()
                        logger.debug(f"🔄 Light refresh of: {current_url}")
                        sb.cdp.open(current_url)
                    except Exception as refresh_error:
                        logger.debug(f"Refresh error (non-critical): {refresh_error}")
                    
                    time.sleep(backoff * attempt)
                else:
                    logger.error(f"💥 All select attempts failed for: {selector}")
                    raise
        
        return None
    
    def extract_job_data(self, item, index: int) -> Optional[Dict[str, str]]:
        """
        Extract job data from a single job element with comprehensive error handling
        """
        try:
            logger.debug(f"📋 Extracting job data for item {index}")
            
            # Extract title with multiple fallback selectors
            title = "N/A"
            title_selectors = [
                'h2 span[title]',
                'h2 span',
                'h2 a span',
                'h2',
                '[data-testid="job-title"]',
                '.jobTitle'
            ]
            
            for selector in title_selectors:
                try:
                    title_el = item.query_selector(selector)
                    if title_el:
                        title_text = title_el.get_attribute("title") or title_el.text
                        if title_text and title_text.strip():
                            title = title_text.strip()
                            logger.debug(f"✅ Title found with {selector}: {title[:50]}...")
                            break
                except Exception as e:
                    logger.debug(f"Title selector {selector} failed: {e}")
                    continue
            
            # Extract company with multiple fallback selectors
            company = "N/A"
            company_selectors = [
                'span[data-testid="company-name"]',
                '[data-testid="company-name"]',
                '.companyName',
                'span.companyName',
                'a .companyName'
            ]
            
            for selector in company_selectors:
                try:
                    company_el = item.query_selector(selector)
                    if company_el:
                        company_text = company_el.text
                        if company_text and company_text.strip():
                            company = company_text.strip()
                            logger.debug(f"✅ Company found with {selector}: {company}")
                            break
                except Exception as e:
                    logger.debug(f"Company selector {selector} failed: {e}")
                    continue
            
            # Extract location with multiple fallback selectors
            job_location = "N/A"
            location_selectors = [
                'div[data-testid="text-location"]',
                '[data-testid="job-location"]',
                '.companyLocation',
                'span.companyLocation'
            ]
            
            for selector in location_selectors:
                try:
                    loc_el = item.query_selector(selector)
                    if loc_el:
                        loc_text = loc_el.text
                        if loc_text and loc_text.strip():
                            job_location = loc_text.strip()
                            logger.debug(f"✅ Location found with {selector}: {job_location}")
                            break
                except Exception as e:
                    logger.debug(f"Location selector {selector} failed: {e}")
                    continue
            
            # Extract link with multiple fallback selectors
            link = "N/A"
            link_selectors = [
                'a.jcs-JobTitle',
                'h2 a',
                'a[data-jk]',
                'a[href*="/viewjob"]'
            ]
            
            for selector in link_selectors:
                try:
                    link_el = item.query_selector(selector)
                    if link_el:
                        href = link_el.get_attribute("href")
                        if href:
                            link = href if href.startswith("http") else f"https://www.indeed.com{href}"
                            logger.debug(f"✅ Link found with {selector}: {link[:50]}...")
                            break
                except Exception as e:
                    logger.debug(f"Link selector {selector} failed: {e}")
                    continue
            
            # Only add jobs with valid titles
            if title != "N/A" and len(title) > 2:
                job_data = {
                    "Title": title,
                    "Company": company,
                    "Location": job_location,
                    "Link": link
                }
                logger.info(f"✅ Job {index} extracted: {title} at {company}")
                return job_data
            else:
                logger.warning(f"⚠️ Job {index} skipped: invalid title")
                return None
                
        except Exception as e:
            logger.error(f"❌ Job extraction error for item {index}: {str(e)}")
            self.scraping_stats['errors_encountered'] += 1
            return None
    
    def scrape_jobs(self, job_title: str, location: str = "Remote", max_pages: int = 1) -> Dict:
        """
        Main scraping function using CDP mode with comprehensive logging
        """
        logger.info("🚀 Starting job scraping process")
        logger.info(f"📋 Parameters: job_title='{job_title}', location='{location}', max_pages={max_pages}")
        
        # Initialize scraping session
        self.jobs_data = []
        self.scraping_stats = {
            'start_time': datetime.now(),
            'end_time': None,
            'pages_attempted': 0,
            'pages_completed': 0,
            'jobs_found': 0,
            'errors_encountered': 0
        }
        
        pages_scraped = 0
        agent = next(self.ua_cycle)
        
        # Use exact same parameters as working script
        sb_kwargs = {
            "uc": True, 
            "test": True, 
            "locale": "en", 
            "ad_block": True, 
            "agent": agent,
            "headless": False  # Keep visible for debugging
        }
        
        logger.info(f"🌐 Using User Agent: {agent}")
        logger.info(f"⚙️ SeleniumBase config: {sb_kwargs}")
        
        try:
            with SB(**sb_kwargs) as sb:
                logger.info("🌍 Opening Indeed.com")
                url = "https://www.indeed.com/"
                sb.activate_cdp_mode(url)
                logger.info("✅ CDP mode activated")
                self.human_sleep(1.5, 3.0)
                
                # Handle captcha if present
                logger.info("🛡️ Checking for captcha...")
                try:
                    sb.uc_gui_click_captcha()
                    logger.info("✅ Captcha handled successfully")
                    self.human_sleep(1.0, 2.0)
                except Exception as e:
                    logger.info(f"ℹ️ No captcha found or auto-handled: {e}")
                
                # Search for jobs using CDP methods
                logger.info("🔍 Filling search form...")
                try:
                    logger.debug("📝 Entering job title")
                    sb.cdp.press_keys('input[id="text-input-what"]', job_title)
                    self.human_sleep(0.8, 1.6)
                    
                    logger.debug("📍 Entering location")
                    sb.cdp.press_keys('input[id="text-input-where"]', location)
                    self.human_sleep(0.6, 1.2)
                    
                    logger.debug("🚀 Submitting search")
                    sb.cdp.click('button[type="submit"]')
                    self.human_sleep(2.5, 4.0)
                    
                    logger.info("✅ Search form submitted successfully")
                    
                except Exception as e:
                    logger.error(f"❌ Search form interaction failed: {str(e)}")
                    return {
                        "success": False,
                        "message": f"Search form interaction failed: {str(e)}",
                        "jobs": [],
                        "total_jobs": 0,
                        "pages_scraped": 0
                    }
                
                # Scrape pages
                page = 1
                while page <= max_pages:
                    logger.info(f"📄 Scraping Page {page}/{max_pages}")
                    self.scraping_stats['pages_attempted'] += 1
                    
                    try:
                        # Wait for page to load
                        logger.debug("⏳ Waiting for job listings to load")
                        time.sleep(2.0)
                        
                        # Use exact same selectors as working script
                        candidate_selectors = [
                            'li.css-5lfssm',                # job card list item (most common)
                            'div.job_seen_beacon',          # alternative Indeed wrapper
                            'div.slider_container',         # fallback
                            '[data-jk]',                    # job key attribute
                            '.jobsearch-SerpJobCard'        # classic job card
                        ]
                        
                        job_elements = None
                        selected_selector = None
                        
                        for sel in candidate_selectors:
                            try:
                                logger.debug(f"🔍 Trying selector: {sel}")
                                job_elements = self.try_select_all_with_retries(sb, sel, retries=2)
                                if job_elements and len(job_elements) > 0:
                                    selected_selector = sel
                                    logger.info(f"✅ Found {len(job_elements)} job elements with: {sel}")
                                    break
                            except Exception as selector_error:
                                logger.debug(f"❌ Selector {sel} failed: {selector_error}")
                                continue
                        
                        if not job_elements or len(job_elements) == 0:
                            logger.warning("⚠️ No job elements found with any selector")
                            if page == 1:
                                logger.error("💥 No jobs found on first page - scraping failed")
                                return {
                                    "success": False,
                                    "message": "No job listings found. The page structure may have changed.",
                                    "jobs": [],
                                    "total_jobs": 0,
                                    "pages_scraped": 0
                                }
                            else:
                                logger.info("ℹ️ No more jobs found, ending pagination")
                                break
                        
                        # Extract job data
                        logger.info(f"📊 Processing {len(job_elements)} job elements")
                        jobs_found_this_page = 0
                        
                        for i, item in enumerate(job_elements, start=1):
                            job_data = self.extract_job_data(item, i)
                            if job_data:
                                self.jobs_data.append(job_data)
                                jobs_found_this_page += 1
                        
                        pages_scraped = page
                        self.scraping_stats['pages_completed'] += 1
                        self.scraping_stats['jobs_found'] = len(self.jobs_data)
                        
                        logger.info(f"✅ Page {page} completed: {jobs_found_this_page} jobs extracted")
                        logger.info(f"📊 Total jobs so far: {len(self.jobs_data)}")
                        
                        # Try clicking next page
                        if page < max_pages:
                            logger.info(f"➡️ Attempting to navigate to page {page + 1}")
                            try:
                                next_btn_selector = 'a[data-testid="pagination-page-next"]'
                                next_btn = sb.cdp.select(next_btn_selector)
                                
                                if next_btn:
                                    logger.debug("🔄 Next button found, clicking...")
                                    sb.cdp.click(next_btn_selector)
                                    self.human_sleep(2.5, 4.5)
                                    page += 1
                                    logger.info(f"✅ Successfully navigated to page {page}")
                                else:
                                    logger.info("🏁 No next button found - reached end of results")
                                    break
                                    
                            except Exception as e:
                                logger.warning(f"❌ Next page navigation failed: {str(e)}")
                                logger.info("🏁 Pagination ended due to navigation failure")
                                break
                        else:
                            logger.info(f"🏁 Reached maximum pages ({max_pages})")
                            break
                            
                    except Exception as e:
                        logger.error(f"❌ Page-level error on page {page}: {str(e)}")
                        self.scraping_stats['errors_encountered'] += 1
                        break
        
        except Exception as e:
            logger.error(f"💥 Top-level scraping error: {str(e)}")
            logger.error(f"🔍 Error type: {type(e).__name__}")
            
            self.scraping_stats['end_time'] = datetime.now()
            
            return {
                "success": False,
                "message": f"Scraping failed: {str(e)}",
                "jobs": self.jobs_data,
                "total_jobs": len(self.jobs_data),
                "pages_scraped": pages_scraped
            }
        
        # Finalize scraping session
        self.scraping_stats['end_time'] = datetime.now()
        duration = self.scraping_stats['end_time'] - self.scraping_stats['start_time']
        
        logger.info("🎉 Scraping session completed!")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"  ⏱️ Duration: {duration.total_seconds():.2f} seconds")
        logger.info(f"  📄 Pages attempted: {self.scraping_stats['pages_attempted']}")
        logger.info(f"  ✅ Pages completed: {self.scraping_stats['pages_completed']}")
        logger.info(f"  🎯 Jobs found: {len(self.jobs_data)}")
        logger.info(f"  ❌ Errors encountered: {self.scraping_stats['errors_encountered']}")
        
        success_rate = (self.scraping_stats['pages_completed'] / max(self.scraping_stats['pages_attempted'], 1)) * 100
        logger.info(f"  📈 Success rate: {success_rate:.1f}%")
        
        return {
            "success": True,
            "message": f"Successfully scraped {len(self.jobs_data)} jobs from {pages_scraped} pages in {duration.total_seconds():.1f}s",
            "jobs": self.jobs_data,
            "total_jobs": len(self.jobs_data),
            "pages_scraped": pages_scraped,
            "scraping_stats": {
                "duration_seconds": duration.total_seconds(),
                "success_rate": success_rate,
                "errors_encountered": self.scraping_stats['errors_encountered']
            }
        }

# Test execution
if __name__ == "__main__":
    logger.info("🧪 Running scraper test")
    scraper = IndeedScraper()
    result = scraper.scrape_jobs("Software Engineer", "Remote", max_pages=2)
    
    print("\n" + "="*50)
    print("SCRAPING RESULTS")
    print("="*50)
    print(json.dumps(result, indent=2))