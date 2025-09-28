# backend/app/scraper.py
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
    
    def try_select_all_with_retries(self, sb, selector, retries=3, backoff=1.2):
        """Retry sb.cdp.select_all with small backoff/refresh to handle timing issues"""
        for attempt in range(1, retries + 1):
            try:
                elements = sb.cdp.select_all(selector)
                return elements
            except Exception as e:
                print(f"⚠️ select_all attempt {attempt} failed: {e}")
                if attempt < retries:
                    self.human_sleep(1.0, 2.5)
                    try:
                        sb.cdp.scroll_into_view("body")
                    except Exception:
                        pass
                    # optional light refresh (avoid heavy reloads often)
                    try:
                        sb.cdp.open(sb.get_current_url())
                    except Exception:
                        pass
                    time.sleep(backoff * attempt)
                else:
                    raise
    
    def scrape_jobs(self, job_title: str, location: str = "Remote", max_pages: int = 1) -> Dict:
        """Main scraping function - Based on working script"""
        self.jobs_data = []
        pages_scraped = 0
        agent = next(self.ua_cycle)
        
        # Use exact same parameters as working script
        sb_kwargs = {
            "uc": True, 
            "test": True, 
            "locale": "en", 
            "ad_block": True, 
            "agent": agent
        }
        
        print(f"Using UA: {agent}")
        
        try:
            with SB(**sb_kwargs) as sb:
                url = "https://www.indeed.com/"
                sb.activate_cdp_mode(url)  # This should work with correct SB version
                self.human_sleep(1.5, 3.0)
                
                # Handle captcha if present
                try:
                    sb.uc_gui_click_captcha()
                    self.human_sleep(1.0, 2.0)
                except Exception as e:
                    print("uc_gui_click_captcha() didn't run automatically:", e)
                
                # Search for jobs using CDP methods (exactly like working script)
                try:
                    sb.cdp.press_keys('input[id="text-input-what"]', job_title)
                    self.human_sleep(0.8, 1.6)
                    sb.cdp.press_keys('input[id="text-input-where"]', location)
                    self.human_sleep(0.6, 1.2)
                    sb.cdp.click('button[type="submit"]')
                    self.human_sleep(2.5, 4.0)
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Search form interaction failed: {str(e)}",
                        "jobs": [],
                        "total_jobs": 0,
                        "pages_scraped": 0
                    }
                
                # Scrape pages (following exact pattern of working script)
                page = 1
                while page <= max_pages:
                    print(f"\n🌍 Scraping Page {page}...")
                    try:
                        # Use exact same selectors as working script
                        candidate_selectors = [
                            'li.css-5lfssm',                # job card list item (common)
                            'div.job_seen_beacon',          # alternative Indeed wrapper
                            'div.slider_container'          # fallbacks
                        ]
                        
                        job_elements = None
                        for sel in candidate_selectors:
                            try:
                                job_elements = self.try_select_all_with_retries(sb, sel, retries=3)
                                if job_elements:
                                    print(f"Selector '{sel}' returned {len(job_elements)} elements")
                                    break
                            except Exception:
                                continue
                        
                        if not job_elements:
                            print("🚫 No job elements found with candidate selectors. Stopping.")
                            break
                        
                        # Extract job data (exact same logic as working script)
                        for i, item in enumerate(job_elements, start=1):
                            try:
                                title_el = item.query_selector('h2 span') or item.query_selector('h2')
                                title = title_el.text.strip() if title_el else "N/A"
                                
                                company_el = item.query_selector('span[data-testid="company-name"]')
                                company = company_el.text.strip() if company_el else "N/A"
                                
                                loc_el = item.query_selector('div[data-testid="text-location"]')
                                job_location = loc_el.text.strip() if loc_el else "N/A"
                                
                                link = ""
                                link_el = item.query_selector('a.jcs-JobTitle') or item.query_selector('a')
                                if link_el:
                                    href = link_el.get_attribute("href")
                                    if href:
                                        link = href if href.startswith("http") else f"https://www.indeed.com{href}"
                                
                                self.jobs_data.append({
                                    "Title": title,
                                    "Company": company,
                                    "Location": job_location,
                                    "Link": link
                                })
                            except Exception as e:
                                print(f"⚠️ Item parse error (i={i}): {e}")
                                continue
                        
                        pages_scraped = page
                        
                        # Try clicking next (exact same logic as working script)
                        if page < max_pages:
                            try:
                                next_btn = sb.cdp.select('a[data-testid="pagination-page-next"]')
                                if next_btn:
                                    sb.cdp.click('a[data-testid="pagination-page-next"]')
                                    self.human_sleep(2.5, 4.5)
                                    page += 1
                                    continue
                                else:
                                    print("🚫 No next button found. Done.")
                                    break
                            except Exception as e:
                                print("🚫 Next page click failed:", e)
                                break
                        else:
                            break
                            
                    except Exception as e:
                        print("❌ Unexpected page-level error:", e)
                        break
        
        except Exception as e:
            print(f"\n💥 Top-level crash: {e}")
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
        
x = IndeedScraper() 
if __name__ == "__main__":
    # Example usage
    result = x.scrape_jobs("Software Engineer", "Remote", max_pages=2)
    print(json.dumps(result, indent=1))