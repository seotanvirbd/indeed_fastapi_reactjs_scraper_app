// frontend/src/components/JobScraper.js
import React, { useState } from 'react';

const JobScraper = ({ onScrapeComplete, onScrapeStart, onScrapeError }) => {
  const [formData, setFormData] = useState({
    jobTitle: '',
    location: 'Remote',
    pages: 1
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [validationErrors, setValidationErrors] = useState({});

  const validateForm = () => {
    const errors = {};
    if (!formData.jobTitle.trim()) {
      errors.jobTitle = 'Job title is required';
    } else if (formData.jobTitle.trim().length < 2) {
      errors.jobTitle = 'Job title must be at least 2 characters';
    }
    if (formData.pages < 1 || formData.pages > 10) {
      errors.pages = 'Pages must be between 1 and 10';
    }
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    const newValue = name === 'pages' ? parseInt(value) || 1 : value;

    setFormData(prev => ({ ...prev, [name]: newValue }));
    if (validationErrors[name]) {
      setValidationErrors(prev => ({ ...prev, [name]: undefined }));
    }
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('🚀 Scraping request submitted');

    if (!validateForm()) {
      console.error('❌ Validation failed');
      return;
    }

    setIsLoading(true);
    setError('');
    onScrapeStart();

    try {
      const { scrapeJobs } = await import('../services/api');
      const result = await scrapeJobs(formData.jobTitle, formData.location, formData.pages);

      console.log('✅ API call successful');
      if (result.success) {
        onScrapeComplete(result);
      } else {
        console.error('⚠️ Scraping finished with issues:', result.message);
        const errorMessage = result.message || 'Scraping failed';
        setError(errorMessage);
        if (onScrapeError) onScrapeError(new Error(errorMessage));
      }
    } catch (err) {
      console.error('❌ API call failed:', err.message);
      const errorMessage = `Error: ${err.response?.data?.detail || err.message}`;
      setError(errorMessage);
      if (onScrapeError) onScrapeError(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="scraper-form">
      <h2>🔍 Indeed Job Scraper</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="jobTitle">
            Job Title <span style={{color: '#e53e3e'}}>*</span>
          </label>
          <input
            type="text"
            id="jobTitle"
            name="jobTitle"
            value={formData.jobTitle}
            onChange={handleInputChange}
            placeholder="e.g., Python Developer, Data Scientist"
            required
            style={{ borderColor: validationErrors.jobTitle ? '#e53e3e' : '#e2e8f0' }}
          />
          {validationErrors.jobTitle && (
            <div style={{color: '#e53e3e', fontSize: '0.9em', marginTop: '4px'}}>
              {validationErrors.jobTitle}
            </div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="location">Location</label>
          <input
            type="text"
            id="location"
            name="location"
            value={formData.location}
            onChange={handleInputChange}
            placeholder="e.g., Remote, New York NY"
          />
        </div>

        <div className="form-group">
          <label htmlFor="pages">Pages to Scrape</label>
          <input
            type="number"
            id="pages"
            name="pages"
            value={formData.pages}
            onChange={handleInputChange}
            min="1"
            max="10"
            style={{ borderColor: validationErrors.pages ? '#e53e3e' : '#e2e8f0' }}
          />
          {validationErrors.pages && (
            <div style={{color: '#e53e3e', fontSize: '0.9em', marginTop: '4px'}}>
              {validationErrors.pages}
            </div>
          )}
        </div>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        <button type="submit" disabled={isLoading} className="scrape-btn">
          {isLoading ? (
            <>
              <span>🔄 Scraping...</span>
              <div style={{fontSize: '0.9em', marginTop: '4px', opacity: 0.8}}>
                Please wait, this may take up to 5 minutes
              </div>
            </>
          ) : (
            <>🚀 Start Scraping</>
          )}
        </button>
      </form>
    </div>
  );
};

export default JobScraper;
