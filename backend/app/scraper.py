# backend/app/scraper_fallback.py
from seleniumbase import SB
import pandas as pd
import json
import time
import random
import sys
from itertools import cycle
from typing import List, Dict

# Rotate realistic user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]

class IndeedScraper:
    def __init__(self):
        self.ua_cycle = cycle(USER_AGENTS)
        self.jobs_data = []
        
    def human_sleep(self, min_s=0.6, max_s=2.0):
        """Human-like sleep delays"""
        time.sleep(random.uniform(min_s, max_s))
    
    def scrape_jobs(self, job_title: str, location: str = "Remote", max_pages: int = 1) -> Dict:
        """Main scraping function using UC Mode only"""
        self.jobs_data = []
        pages_scraped = 0
        agent = next(self.ua_cycle)
        
        # UC mode without CDP
        sb_kwargs = {
            "uc": True,
            "headless": False,  # Keep visible for debugging
            "agent": agent
        }
        
        print(f"Using UA: {agent}")
        
        try:
            with SB(**sb_kwargs) as sb:
                url = "https://www.indeed.com/"
                sb.open(url)
                self.human_sleep(1.5, 3.0)
                
                # Handle captcha if present
                try:
                    sb.uc_gui_click_captcha()
                    self.human_sleep(1.0, 2.0)
                except Exception as e:
                    print("uc_gui_click_captcha() didn't run automatically:", e)
                
                # Search for jobs using regular selenium methods
                try:
                    # Try multiple selectors for job input
                    job_input_found = False
                    job_selectors = [
                        'input[id="text-input-what"]',
                        'input[name="q"]',
                        'input[data-testid="job-search-bar-keywords-input"]'
                    ]
                    
                    for selector in job_selectors:
                        try:
                            if sb.is_element_visible(selector):
                                sb.type(selector, job_title)
                                job_input_found = True
                                break
                        except Exception:
                            continue
                    
                    if not job_input_found:
                        raise Exception("Could not find job title input")
                    
                    self.human_sleep(0.8, 1.6)
                    
                    # Try multiple selectors for location input
                    location_selectors = [
                        'input[id="text-input-where"]',
                        'input[name="l"]',
                        'input[data-testid="job-search-bar-location-input"]'
                    ]
                    
                    for selector in location_selectors:
                        try:
                            if sb.is_element_visible(selector):
                                sb.clear(selector)
                                sb.type(selector, location)
                                break
                        except Exception:
                            continue
                    
                    self.human_sleep(0.6, 1.2)
                    
                    # Submit search
                    submit_selectors = [
                        'button[type="submit"]',
                        'button[data-testid="job-search-bar-submit"]'
                    ]
                    
                    for selector in submit_selectors:
                        try:
                            if sb.is_element_visible(selector):
                                sb.click(selector)
                                break
                        except Exception:
                            continue
                    
                    self.human_sleep(2.5, 4.0)
                    
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Search failed: {str(e)}",
                        "jobs": [],
                        "total_jobs": 0,
                        "pages_scraped": 0
                    }
                
                # Scrape pages
                page = 1
                while page <= max_pages:
                    print(f"\n🌍 Scraping Page {page}...")
                    
                    try:
                        # Wait for job results to load
                        sb.wait_for_element_visible('[data-jk]', timeout=10)
                        
                        # Find job elements
                        candidate_selectors = [
                            '[data-testid="job-tile"]',
                            
                            '.job_seen_beacon',
                            '[data-jk]',
                            '.result',
                            '.jobsearch-SerpJobCard',
                            'li.css-5lfssm'
                        ]
                        
                        job_elements = []
                        for sel in candidate_selectors:
                            try:
                                elements = sb.find_elements(sel)
                                if elements:
                                    job_elements = elements
                                    print(f"Found {len(job_elements)} job elements with selector: {sel}")
                                    break
                            except Exception:
                                continue
                        
                        if not job_elements:
                            print("❌ No job elements found")
                            break
                        
                        # Extract job data
                        for i, element in enumerate(job_elements):
                            try:
                                # Extract title
                                title = "N/A"
                                title_selectors = [
                                    'h2 a span[title]',
                                    'h2 span[title]',
                                    'h2 a',
                                    'h2',
                                    '[data-testid="job-title"]'
                                ]
                                
                                for sel in title_selectors:
                                    try:
                                        title_el = element.find_element("css selector", sel)
                                        title_text = title_el.get_attribute("title") or title_el.text
                                        if title_text and title_text.strip():
                                            title = title_text.strip()
                                            break
                                    except Exception:
                                        continue
                                
                                # Extract company
                                company = "N/A"
                                company_selectors = [
                                    'span[data-testid="company-name"]',
                                    '[data-testid="company-name"]',
                                    '.companyName'
                                ]
                                
                                for sel in company_selectors:
                                    try:
                                        company_el = element.find_element("css selector", sel)
                                        company_text = company_el.text
                                        if company_text and company_text.strip():
                                            company = company_text.strip()
                                            break
                                    except Exception:
                                        continue
                                
                                # Extract location
                                job_location = "N/A"
                                location_selectors = [
                                    '[data-testid="job-location"]',
                                    'div[data-testid="text-location"]',
                                    '.companyLocation'
                                ]
                                
                                for sel in location_selectors:
                                    try:
                                        loc_el = element.find_element("css selector", sel)
                                        loc_text = loc_el.text
                                        if loc_text and loc_text.strip():
                                            job_location = loc_text.strip()
                                            break
                                    except Exception:
                                        continue
                                
                                # Extract link
                                link = "N/A"
                                link_selectors = [
                                    'h2 a',
                                    'a[data-jk]',
                                    'a[href*="/viewjob"]'
                                ]
                                
                                for sel in link_selectors:
                                    try:
                                        link_el = element.find_element("css selector", sel)
                                        href = link_el.get_attribute("href")
                                        if href:
                                            link = href if href.startswith("http") else f"https://www.indeed.com{href}"
                                            break
                                    except Exception:
                                        continue
                                
                                # Only add jobs with valid titles
                                if title != "N/A" and len(title) > 2:
                                    self.jobs_data.append({
                                        "Title": title,
                                        "Company": company,
                                        "Location": job_location,
                                        "Link": link
                                    })
                                
                            except Exception as e:
                                print(f"⚠️ Error extracting job {i}: {e}")
                                continue
                        
                        pages_scraped = page
                        print(f"✅ Page {page} complete. Total jobs: {len(self.jobs_data)}")
                        
                        # Try to go to next page
                        if page < max_pages:
                            try:
                                next_selectors = [
                                    'a[data-testid="pagination-page-next"]',
                                    'a[aria-label="Next Page"]',
                                    'a[aria-label="Next"]'
                                ]
                                
                                next_clicked = False
                                for sel in next_selectors:
                                    try:
                                        if sb.is_element_visible(sel):
                                            sb.click(sel)
                                            next_clicked = True
                                            break
                                    except Exception:
                                        continue
                                
                                if next_clicked:
                                    self.human_sleep(2.5, 4.5)
                                    page += 1
                                else:
                                    print("❌ No next button found")
                                    break
                            except Exception as e:
                                print(f"❌ Next page failed: {e}")
                                break
                        else:
                            break
                            
                    except Exception as e:
                        print(f"❌ Page scraping error: {e}")
                        break
        
        except Exception as e:
            print(f"\n💥 Scraping failed: {e}")
            return {
                "success": False,
                "message": f"Scraping failed: {str(e)}",
                "jobs": [],
                "total_jobs": 0,
                "pages_scraped": pages_scraped
            }
        
        return {
            "success": True,
            "message": f"Successfully scraped {len(self.jobs_data)} jobs from {pages_scraped} pages",
            "jobs": self.jobs_data,
            "total_jobs": len(self.jobs_data),
            "pages_scraped": pages_scraped
        }
        
# x=IndeedScraper()
# y=x.scrape_jobs("data scientist","remote",2)    
# print(y)