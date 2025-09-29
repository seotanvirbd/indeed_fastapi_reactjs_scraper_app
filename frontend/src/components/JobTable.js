// frontend/src/components/JobTable.js
import React, { useState, useEffect, useMemo } from 'react';

const JobTable = ({ jobs, totalJobs, pagesScraped, success, message }) => {
  const [sortField, setSortField] = useState('');
  const [sortDirection, setSortDirection] = useState('asc');
  const [filterText, setFilterText] = useState('');

  // Debug logging
  useEffect(() => {
    console.group('📊 JobTable Component Updated');
    console.log('Jobs received:', jobs?.length || 0);
    console.log('Total jobs:', totalJobs);
    console.log('Pages scraped:', pagesScraped);
    console.log('Success status:', success);
    console.log('Message:', message);
    console.groupEnd();
  }, [jobs, totalJobs, pagesScraped, success, message]);

  // Analytics calculations
  const analytics = useMemo(() => {
    if (!jobs || jobs.length === 0) return null;

    console.log('🔍 Calculating job analytics...');
    
    const companies = {};
    const locations = {};
    const validLinks = jobs.filter(job => job.Link && job.Link !== 'N/A').length;

    jobs.forEach(job => {
      // Company analysis
      const company = job.Company || 'Unknown';
      companies[company] = (companies[company] || 0) + 1;

      // Location analysis
      const location = job.Location || 'Unknown';
      locations[location] = (locations[location] || 0) + 1;
    });

    const topCompanies = Object.entries(companies)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3);

    const topLocations = Object.entries(locations)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3);

    const result = {
      totalJobs: jobs.length,
      uniqueCompanies: Object.keys(companies).length,
      uniqueLocations: Object.keys(locations).length,
      validLinksPercentage: Math.round((validLinks / jobs.length) * 100),
      topCompanies,
      topLocations
    };

    console.log('📈 Analytics calculated:', result);
    return result;
  }, [jobs]);

  // Filtered and sorted jobs
  const processedJobs = useMemo(() => {
    if (!jobs) return [];

    let filtered = jobs;

    // Apply filter
    if (filterText.trim()) {
      filtered = jobs.filter(job =>
        job.Title?.toLowerCase().includes(filterText.toLowerCase()) ||
        job.Company?.toLowerCase().includes(filterText.toLowerCase()) ||
        job.Location?.toLowerCase().includes(filterText.toLowerCase())
      );
      console.log(`🔍 Filtered jobs: ${filtered.length}/${jobs.length} (filter: "${filterText}")`);
    }

    // Apply sort
    if (sortField) {
      filtered = [...filtered].sort((a, b) => {
        const aVal = a[sortField] || '';
        const bVal = b[sortField] || '';
        const comparison = aVal.toString().localeCompare(bVal.toString());
        return sortDirection === 'asc' ? comparison : -comparison;
      });
      console.log(`📊 Sorted by ${sortField} (${sortDirection})`);
    }

    return filtered;
  }, [jobs, filterText, sortField, sortDirection]);

  const handleSort = (field) => {
    console.log(`🔄 Sorting by: ${field}`);
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleFilterChange = (e) => {
    const value = e.target.value;
    console.log(`🔍 Filter changed: "${value}"`);
    setFilterText(value);
  };

  if (!jobs || jobs.length === 0) {
    return (
      <div className="no-data">
        <div style={{ fontSize: '3em', marginBottom: '16px' }}>📭</div>
        <p style={{ fontSize: '1.1em', marginBottom: '8px' }}>
          {success === false ? 'Scraping encountered issues' : 'No jobs found'}
        </p>
        {message && (
          <p style={{ fontSize: '0.95em', opacity: 0.8 }}>
            {message}
          </p>
        )}
        <p style={{ fontSize: '0.9em', marginTop: '16px', opacity: 0.7 }}>
          Try scraping with different parameters or check your internet connection
        </p>
      </div>
    );
  }

  return (
    <div className="job-table-container">
      {/* Header with Analytics */}
      <div className="table-header">
        <h3>
          📋 Scraped Jobs Results
          <span className="status-badge success" style={{ marginLeft: '12px', fontSize: '0.7em' }}>
            {totalJobs} Total
          </span>
        </h3>
        
        {analytics && (
          <div style={{
            background: '#f7fafc',
            padding: '16px',
            borderRadius: '12px',
            marginBottom: '20px',
            fontSize: '0.9em'
          }}>
            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', marginBottom: '12px' }}>
              <div><strong>📊 Jobs Found:</strong> {analytics.totalJobs}</div>
              <div><strong>🏢 Unique Companies:</strong> {analytics.uniqueCompanies}</div>
              <div><strong>📍 Unique Locations:</strong> {analytics.uniqueLocations}</div>
              <div><strong>🔗 Valid Links:</strong> {analytics.validLinksPercentage}%</div>
            </div>
            
            {analytics.topCompanies.length > 0 && (
              <div style={{ fontSize: '0.85em', opacity: 0.8 }}>
                <strong>Top Companies:</strong> {analytics.topCompanies.map(([company, count]) => 
                  `${company} (${count})`
                ).join(', ')}
              </div>
            )}
          </div>
        )}

        {/* Search Filter */}
        <div style={{ marginBottom: '20px' }}>
          <input
            type="text"
            placeholder="🔍 Filter jobs by title, company, or location..."
            value={filterText}
            onChange={handleFilterChange}
            style={{
              width: '100%',
              maxWidth: '400px',
              padding: '12px 16px',
              border: '2px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '0.95em'
            }}
          />
        </div>
      </div>
      
      <div className="table-wrapper">
        <table className="job-table">
          <thead>
            <tr>
              <th>#</th>
              <th 
                onClick={() => handleSort('Title')} 
                style={{ cursor: 'pointer', userSelect: 'none' }}
              >
                Job Title {sortField === 'Title' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th 
                onClick={() => handleSort('Company')} 
                style={{ cursor: 'pointer', userSelect: 'none' }}
              >
                Company {sortField === 'Company' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th 
                onClick={() => handleSort('Location')} 
                style={{ cursor: 'pointer', userSelect: 'none' }}
              >
                Location {sortField === 'Location' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {processedJobs.map((job, index) => (
              <tr key={`${job.Title}-${job.Company}-${index}`}>
                <td>{index + 1}</td>
                <td className="job-title">
                  {job.Title || 'No Title'}
                  {job.Title && job.Title.length > 50 && (
                    <div style={{ fontSize: '0.8em', opacity: 0.7, marginTop: '4px' }}>
                      {job.Title.substring(0, 50)}...
                    </div>
                  )}
                </td>
                <td>
                  {job.Company || 'Unknown Company'}
                </td>
                <td>
                  {job.Location || 'Location Not Specified'}
                </td>
                <td>
                  {job.Link && job.Link !== 'N/A' ? (
                    <a 
                      href={job.Link} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="job-link"
                      onClick={() => {
                        console.log('🔗 Job link clicked:', {
                          title: job.Title,
                          company: job.Company,
                          link: job.Link
                        });
                      }}
                    >
                      View Job
                    </a>
                  ) : (
                    <span style={{ 
                      color: '#a0aec0', 
                      fontSize: '0.9em',
                      fontStyle: 'italic'
                    }}>
                      No Link
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer Summary */}
      <div style={{
        marginTop: '16px',
        padding: '12px',
        background: '#f7fafc',
        borderRadius: '8px',
        fontSize: '0.9em',
        color: '#4a5568',
        textAlign: 'center'
      }}>
        {filterText ? (
          <>
            Showing {processedJobs.length} of {jobs.length} jobs 
            (filtered by "{filterText}")
          </>
        ) : (
          <>
            Showing all {jobs.length} jobs from {pagesScraped} pages
          </>
        )}
        {sortField && (
          <span> • Sorted by {sortField} ({sortDirection === 'asc' ? 'A-Z' : 'Z-A'})</span>
        )}
      </div>

      {/* Debug Info in Development */}
      {process.env.NODE_ENV === 'development' && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          background: '#fffaf0',
          borderRadius: '8px',
          fontSize: '0.8em',
          color: '#744210'
        }}>
          <strong>Debug Info:</strong><br/>
          Original Jobs: {jobs?.length || 0}<br/>
          Processed Jobs: {processedJobs.length}<br/>
          Filter Active: {filterText ? `"${filterText}"` : 'None'}<br/>
          Sort: {sortField ? `${sortField} (${sortDirection})` : 'None'}<br/>
          Render Time: {new Date().toLocaleTimeString()}
        </div>
      )}
    </div>
  );
};

export default JobTable;