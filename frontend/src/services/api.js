// frontend/src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json',
  }
});

/**
 * Scrape jobs from Indeed
 */
export const scrapeJobs = async (jobTitle, location = 'Remote', pages = 1) => {
  console.log('🎯 Starting scraping request...');

  try {
    if (!jobTitle || typeof jobTitle !== 'string' || jobTitle.trim().length === 0) {
      throw new Error('Job title is required and must be a non-empty string');
    }
    if (pages < 1 || pages > 10) {
      throw new Error('Pages must be between 1 and 10');
    }

    const requestData = {
      job_title: jobTitle.trim(),
      location: location.trim() || 'Remote',
      pages: parseInt(pages) || 1
    };

    const response = await api.post('/scrape', requestData);

    console.log(`✅ Scraping done. Jobs: ${response.data.total_jobs}, Pages: ${response.data.pages_scraped}`);
    return response.data;

  } catch (error) {
    let errorMessage = 'Scraping failed';

    if (error.response) {
      errorMessage = error.response.data?.detail || error.response.data?.message || `Server error (${error.response.status})`;
    } else if (error.code === 'ECONNABORTED') {
      errorMessage = 'Request timed out. Scraping took too long.';
    } else if (error.code === 'ECONNREFUSED') {
      errorMessage = 'Cannot connect to server. Make sure backend is running.';
    } else if (error.message) {
      errorMessage = error.message;
    }

    console.error('❌ Scraping failed:', errorMessage);
    const enhancedError = new Error(errorMessage);
    enhancedError.originalError = error;
    enhancedError.response = error.response;
    throw enhancedError;
  }
};

/**
 * Download scraped jobs in specified format
 */
export const downloadFile = async (format) => {
  console.log(`💾 Downloading file: ${format.toUpperCase()}`);

  try {
    const validFormats = ['csv', 'excel', 'json'];
    if (!validFormats.includes(format)) {
      throw new Error(`Invalid format: ${format}`);
    }

    const response = await api.get(`/download/${format}`, {
      responseType: 'blob',
      headers: {
        'Accept': format === 'json' ? 'application/json' : 
                 format === 'excel' ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' :
                 'text/csv'
      }
    });

    console.log(`✅ Download completed (${response.data.size || 0} bytes)`);
    return response.data;

  } catch (error) {
    console.error('❌ Download failed:', error.message || 'Unknown error');
    const enhancedError = new Error('Download failed');
    enhancedError.originalError = error;
    enhancedError.response = error.response;
    throw enhancedError;
  }
};

/**
 * Check API health/status
 */
export const checkServerStatus = async () => {
  try {
    const response = await api.get('/', { timeout: 5000 });
    console.log('✅ Server is online');
    return { online: true, message: response.data.message };
  } catch (error) {
    console.warn('⚠️ Server check failed');
    return { online: false, error: error.message };
  }
};

export { api };
