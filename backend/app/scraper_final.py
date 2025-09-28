# scraper_1.py
from seleniumbase import SB
import pandas as pd
import json
import time
import random
import sys
from itertools import cycle
from typing import List, Dict, Optional

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

    def _has_cdp(self, sb: SB) -> bool:
        return getattr(sb, "cdp", None) is not None

    def _safe_cdp_call(self, sb: SB, fn_name: str, *args, **kwargs):
        """Try to call a CDP method by name, return None on failure."""
        cdp = getattr(sb, "cdp", None)
        if not cdp:
            return None
        fn = getattr(cdp, fn_name, None)
        if not fn:
            return None
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            # swallow and return None so caller can fallback
            print(f"⚠️ cdp.{fn_name} failed: {e}")
            return None

    def try_select_all_with_retries(self, sb: SB, selector: str, retries=3, backoff=1.2):
        """Try to get elements using CDP if available, else fallback to SB find_elements."""
        for attempt in range(1, retries + 1):
            try:
                if self._has_cdp(sb):
                    elems = self._safe_cdp_call(sb, "select_all", selector)
                    if elems:
                        return elems
                    # if CDP returned empty list, let fallback try
                # fallback:
                elements = sb.find_elements(selector)
                if elements:
                    return elements
                # nothing found: small sleep and retry
                self.human_sleep(0.8, 1.5)
            except Exception as e:
                print(f"⚠️ select_all attempt {attempt} failed: {e}")
                self.human_sleep(1.0, 2.0)
                try:
                    # light refresh/scroll to help dynamic pages
                    if self._has_cdp(sb):
                        try:
                            self._safe_cdp_call(sb, "scroll_into_view", "body")
                        except Exception:
                            pass
                except Exception:
                    pass
            time.sleep(backoff * attempt)
        return []

    def _click(self, sb: SB, selector: str):
        """Try CDP click, then fallback to SB.click"""
        if self._has_cdp(sb):
            res = self._safe_cdp_call(sb, "click", selector)
            if res is not None:
                return True
        try:
            if sb.is_element_visible(selector):
                sb.click(selector)
                return True
        except Exception:
            pass
        return False

    def _type(self, sb: SB, selector: str, text: str):
        """Try CDP press_keys, then fallback to sb.type"""
        if self._has_cdp(sb):
            res = self._safe_cdp_call(sb, "press_keys", selector, text)
            if res is not None:
                return True
        try:
            if sb.is_element_visible(selector):
                sb.clear(selector)
                sb.type(selector, text)
                return True
        except Exception:
            pass
        return False

    def scrape_jobs(self, job_title: str, location: str = "Remote", max_pages: int = 1) -> Dict:
        """CDP-first scraper with safe fallbacks."""
        self.jobs_data = []
        pages_scraped = 0
        agent = next(self.ua_cycle)

        sb_kwargs = {
            "uc": True,
            "test": True,
            "locale": "en",
            "ad_block": True,
            "agent": agent,
            # "headless": False  # you can force visible browser for debugging
        }

        print(f"Using UA: {agent}")

        try:
            with SB(**sb_kwargs) as sb:
                url = "https://www.indeed.com/"

                # Try to activate CDP mode if method exists; otherwise open normally
                activated_cdp = False
                if hasattr(sb, "activate_cdp_mode"):
                    try:
                        sb.activate_cdp_mode(url)
                        activated_cdp = True
                        print("✅ activate_cdp_mode() succeeded.")
                    except Exception as e:
                        print("⚠️ activate_cdp_mode() failed:", e)

                if not activated_cdp:
                    # open normally and allow CDP attribute to be present if SB supports it
                    try:
                        sb.open(url)
                    except Exception as e:
                        # final fallback: try to open via cdp if available
                        print("⚠️ sb.open() failed:", e)
                        if self._has_cdp(sb):
                            try:
                                self._safe_cdp_call(sb, "open", url)
                            except Exception as ee:
                                print("⚠️ cdp.open() also failed:", ee)

                self.human_sleep(1.5, 3.0)

                # Handle captcha if present (best-effort; may require manual solve)
                try:
                    sb.uc_gui_click_captcha()
                    self.human_sleep(1.0, 2.0)
                except Exception as e:
                    # ignore; just log
                    print("uc_gui_click_captcha() didn't run automatically:", e)

                # Fill search form (CDP-first, fallback to SB)
                try:
                    typed = self._type(sb, 'input[id="text-input-what"]', job_title)
                    if not typed:
                        # try other selectors like working script
                        self._type(sb, 'input[name="q"]', job_title)
                        self._type(sb, 'input[data-testid="job-search-bar-keywords-input"]', job_title)
                    self.human_sleep(0.8, 1.6)

                    typed_loc = self._type(sb, 'input[id="text-input-where"]', location)
                    if not typed_loc:
                        self._type(sb, 'input[name="l"]', location)
                        self._type(sb, 'input[data-testid="job-search-bar-location-input"]', location)
                    self.human_sleep(0.6, 1.2)

                    submitted = self._click(sb, 'button[type="submit"]') or self._click(sb, 'button[data-testid="job-search-bar-submit"]')
                    if not submitted:
                        print("⚠️ Could not find submit button by primary selectors; attempting ENTER key via CDP if available.")
                        if self._has_cdp(sb):
                            try:
                                self._safe_cdp_call(sb, "press_keys", 'input[id="text-input-what"]', "\n")
                            except Exception:
                                pass

                    self.human_sleep(2.5, 4.0)
                except Exception as e:
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
                    print(f"\n🌍 Scraping Page {page}...")
                    try:
                        candidate_selectors = [
                            'li.css-5lfssm',
                            'div.job_seen_beacon',
                            'div.slider_container',
                            '[data-jk]',
                            '.job_seen_beacon',
                            '.result'
                        ]

                        job_elements = None
                        for sel in candidate_selectors:
                            elems = self.try_select_all_with_retries(sb, sel, retries=3)
                            if elems:
                                job_elements = elems
                                print(f"Selector '{sel}' returned {len(job_elements)} elements")
                                break

                        if not job_elements:
                            print("🚫 No job elements found with candidate selectors. Stopping.")
                            break

                        # Extract job data
                        for i, item in enumerate(job_elements, start=1):
                            try:
                                # For CDP returned elements, they may be wrapper objects with query_selector
                                title = "N/A"
                                company = "N/A"
                                job_location = "N/A"
                                link = "N/A"

                                # Try CDP-style element (has query_selector)
                                if hasattr(item, "query_selector"):
                                    title_el = item.query_selector('h2 span') or item.query_selector('h2')
                                    title = title_el.text.strip() if title_el else title

                                    company_el = item.query_selector('span[data-testid="company-name"]')
                                    company = company_el.text.strip() if company_el else company

                                    loc_el = item.query_selector('div[data-testid="text-location"]')
                                    job_location = loc_el.text.strip() if loc_el else job_location

                                    link_el = item.query_selector('a.jcs-JobTitle') or item.query_selector('a')
                                    if link_el:
                                        href = link_el.get_attribute("href")
                                        if href:
                                            link = href if href.startswith("http") else f"https://www.indeed.com{href}"
                                else:
                                    # Fallback to SB selenium element (WebElement-like)
                                    try:
                                        title_el = item.find_element("css selector", 'h2 span') or item.find_element("css selector", 'h2')
                                        title = (title_el.get_attribute("title") or title_el.text).strip() if title_el else title
                                    except Exception:
                                        pass
                                    try:
                                        company_el = item.find_element("css selector", 'span[data-testid="company-name"]')
                                        company = company_el.text.strip() if company_el else company
                                    except Exception:
                                        pass
                                    try:
                                        loc_el = item.find_element("css selector", 'div[data-testid="text-location"]')
                                        job_location = loc_el.text.strip() if loc_el else job_location
                                    except Exception:
                                        pass
                                    try:
                                        link_el = item.find_element("css selector", 'a.jcs-JobTitle')
                                        href = link_el.get_attribute("href")
                                        if href:
                                            link = href if href.startswith("http") else f"https://www.indeed.com{href}"
                                    except Exception:
                                        pass

                                if title and title != "N/A" and len(title) > 2:
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

                        # Next page
                        if page < max_pages:
                            clicked_next = False
                            # try CDP next
                            if self._has_cdp(sb):
                                res = self._safe_cdp_call(sb, "click", 'a[data-testid="pagination-page-next"]')
                                if res is not None:
                                    clicked_next = True
                            # fallback to SB click
                            if not clicked_next:
                                try:
                                    if sb.is_element_visible('a[data-testid="pagination-page-next"]'):
                                        sb.click('a[data-testid="pagination-page-next"]')
                                        clicked_next = True
                                except Exception:
                                    clicked_next = False

                            if clicked_next:
                                self.human_sleep(2.5, 4.5)
                                page += 1
                                continue
                            else:
                                print("🚫 No next button found. Done.")
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

if __name__ == "__main__":
    x = IndeedScraper()
    result = x.scrape_jobs("Software Engineer", "Remote", max_pages=2)
    print(json.dumps(result, indent=1))
