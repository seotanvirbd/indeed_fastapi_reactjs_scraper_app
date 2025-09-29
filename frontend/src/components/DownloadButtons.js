// frontend/src/components/DownloadButtons.js
import React, { useState } from 'react';

const DownloadButtons = ({ hasData }) => {
  const [downloading, setDownloading] = useState({});
  const [downloadStats, setDownloadStats] = useState({
    totalDownloads: 0,
    lastDownload: null,
    downloadHistory: []
  });

  const handleDownload = async (format) => {
    if (!hasData) {
      console.warn('Download attempted but no data available');
      return;
    }

    console.log(`Starting ${format.toUpperCase()} download`);
    setDownloading(prev => ({ ...prev, [format]: true }));

    try {
      const { downloadFile } = await import('../services/api');
      const blob = await downloadFile(format);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Set filename based on format
      const extensions = { csv: 'csv', excel: 'xlsx', json: 'json' };
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
      const filename = `indeed-jobs-${timestamp}.${extensions[format]}`;
      link.download = filename;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      // Update download statistics
      const downloadInfo = {
        format,
        filename,
        timestamp: new Date().toISOString(),
        size: blob.size
      };

      setDownloadStats(prev => ({
        totalDownloads: prev.totalDownloads + 1,
        lastDownload: downloadInfo,
        downloadHistory: [...prev.downloadHistory, downloadInfo].slice(-10)
      }));

      console.log(`${format.toUpperCase()} download completed: ${filename}`);
      
    } catch (error) {
      console.error(`${format.toUpperCase()} download failed:`, error.message);
      const errorMessage = `Download failed: ${error.response?.data?.detail || error.message}`;
      alert(errorMessage);
    } finally {
      setDownloading(prev => ({ ...prev, [format]: false }));
    }
  };

  const getButtonContent = (format, isDownloading) => {
    const formatInfo = {
      csv: { icon: '📊', label: 'CSV', description: 'Excel Compatible' },
      excel: { icon: '📈', label: 'Excel', description: 'Native Format' },
      json: { icon: '🔗', label: 'JSON', description: 'Developer Friendly' }
    };

    const info = formatInfo[format];
    
    if (isDownloading) {
      return (
        <>
          <div>⏳ Downloading...</div>
          <div style={{ fontSize: '0.8em', opacity: 0.8 }}>Please wait</div>
        </>
      );
    }

    return (
      <>
        <div>{info.icon} Download {info.label}</div>
        <div style={{ fontSize: '0.8em', opacity: 0.8 }}>{info.description}</div>
      </>
    );
  };

  if (!hasData) {
    return (
      <div className="download-section disabled">
        <div style={{ fontSize: '2em', marginBottom: '12px' }}>📄</div>
        <h3>Download Not Available</h3>
        <p style={{ fontSize: '1em', opacity: 0.8 }}>
          Scrape jobs first to enable download functionality
        </p>
        <div className="status-badge error" style={{ marginTop: '12px' }}>
          No Data Available
        </div>
      </div>
    );
  }

  return (
    <div className="download-section">
      <h3>💾 Download Results</h3>
      <p style={{ marginBottom: '24px', opacity: 0.8 }}>
        Export your job data in multiple formats for further analysis
      </p>

      <div className="download-buttons">
        <button
          onClick={() => handleDownload('csv')}
          disabled={downloading.csv}
          className="download-btn csv"
          title="Download as CSV file - Compatible with Excel, Google Sheets"
        >
          {getButtonContent('csv', downloading.csv)}
        </button>
        
        <button
          onClick={() => handleDownload('excel')}
          disabled={downloading.excel}
          className="download-btn excel"
          title="Download as Excel file - Native Excel format with formatting"
        >
          {getButtonContent('excel', downloading.excel)}
        </button>
        
        <button
          onClick={() => handleDownload('json')}
          disabled={downloading.json}
          className="download-btn json"
          title="Download as JSON file - Perfect for developers and API integration"
        >
          {getButtonContent('json', downloading.json)}
        </button>
      </div>

      {/* Download Statistics */}
      {downloadStats.totalDownloads > 0 && (
        <div style={{
          marginTop: '24px',
          padding: '16px',
          background: '#f7fafc',
          borderRadius: '12px',
          fontSize: '0.9em',
          color: '#4a5568'
        }}>
          <div style={{ marginBottom: '8px' }}>
            <strong>📊 Download Statistics</strong>
          </div>
          <div>Total Downloads: {downloadStats.totalDownloads}</div>
          {downloadStats.lastDownload && (
            <div style={{ fontSize: '0.85em', marginTop: '4px', opacity: 0.8 }}>
              Last: {downloadStats.lastDownload.format.toUpperCase()} at{' '}
              {new Date(downloadStats.lastDownload.timestamp).toLocaleTimeString()}
              {' '}({Math.round(downloadStats.lastDownload.size / 1024)} KB)
            </div>
          )}
        </div>
      )}

      {/* Format Information */}
      <div style={{
        marginTop: '20px',
        padding: '16px',
        background: '#fffaf0',
        borderRadius: '12px',
        fontSize: '0.85em',
        color: '#744210'
      }}>
        <div style={{ marginBottom: '12px' }}>
          <strong>📋 Format Guide:</strong>
        </div>
        <div><strong>CSV:</strong> Best for Excel, Google Sheets, and data analysis</div>
        <div><strong>Excel:</strong> Native Excel format with preserved formatting</div>
        <div><strong>JSON:</strong> Perfect for developers and API integrations</div>
      </div>

      {/* Debug Info in Development Mode Only */}
      {process.env.NODE_ENV === 'development' && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          background: '#f0fff4',
          borderRadius: '8px',
          fontSize: '0.8em',
          color: '#22543d'
        }}>
          <strong>Debug Info:</strong><br/>
          Has Data: {hasData ? '✅' : '❌'}<br/>
          Active Downloads: {Object.values(downloading).filter(Boolean).length}<br/>
          Total Session Downloads: {downloadStats.totalDownloads}
        </div>
      )}
    </div>
  );
};

export default DownloadButtons;