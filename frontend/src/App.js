// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import JobScraper from './components/JobScraper';
import JobTable from './components/JobTable';
import DownloadButtons from './components/DownloadButtons';
import './App.css';

function App() {
  const [scrapeResults, setScrapeResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [appStartTime] = useState(new Date());

  useEffect(() => {
    console.log('🚀 Indeed Job Scraper App started at', appStartTime.toISOString());
  }, [appStartTime]);

  const handleScrapeStart = () => {
    console.log('🎯 Scraping started...');
    console.time('Total Scrape Duration');
    setIsLoading(true);
    setScrapeResults(null);
  };

  const handleScrapeComplete = (results) => {
    console.timeEnd('Total Scrape Duration');
    console.log(`✅ Scraping finished. Jobs: ${results?.jobs?.length || 0}`);
    setIsLoading(false);
    setScrapeResults(results);
  };

  const handleScrapeError = (error) => {
    console.timeEnd('Total Scrape Duration');
    console.error('❌ Scraping failed:', error.message);
    setIsLoading(false);
    setScrapeResults({
      success: false,
      message: error.message || 'Unknown error occurred',
      jobs: [],
      total_jobs: 0,
      pages_scraped: 0
    });
  };

  return (
    <div className="App">
      <div className="container">
        <header className="app-header">
          <h1>🎯 Indeed Job Scraper</h1>
          <p>Professional job scraping with analytics and downloads</p>
          <div className="status-badge success" style={{marginTop: '12px'}}>
            Professional Edition
          </div>
        </header>

        <main className="main-content">
          <div className="scraper-section">
            <JobScraper
              onScrapeStart={handleScrapeStart}
              onScrapeComplete={handleScrapeComplete}
              onScrapeError={handleScrapeError}
            />
          </div>

          {isLoading && (
            <div className="loading-section">
              <div className="spinner"></div>
              <p>Scraping jobs from Indeed... This may take a few minutes.</p>
              <div className="status-badge loading" style={{marginTop: '16px'}}>
                Processing
              </div>
            </div>
          )}

          {scrapeResults && (
            <>
              <div className="results-section">
                <JobTable
                  jobs={scrapeResults.jobs}
                  totalJobs={scrapeResults.total_jobs}
                  pagesScraped={scrapeResults.pages_scraped}
                  success={scrapeResults.success}
                  message={scrapeResults.message}
                />
              </div>

              <div className="download-section-wrapper">
                <DownloadButtons hasData={scrapeResults.jobs.length > 0} />
              </div>
            </>
          )}
        </main>

        <footer className="app-footer">
          <p>Built with React + FastAPI | Professional Web Scraping Solution</p>
          <p style={{fontSize: '0.8em', marginTop: '8px', opacity: 0.7}}>
            Session started at {appStartTime.toLocaleTimeString()}
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
