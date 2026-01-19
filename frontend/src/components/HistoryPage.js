import React, { useState, useEffect } from 'react';
import axios from 'axios';

function HistoryPage({ onSelectResume, onBack }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/history/');
      setHistory(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load history');
      console.error('Error loading history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (resumeId) => {
    try {
      const response = await axios.get(`http://localhost:8000/history/${resumeId}`);
      onSelectResume(
        response.data.id,
        response.data.job_title,
        response.data.resume_data
      );
    } catch (err) {
      alert('Error loading resume');
      console.error('Error loading resume:', err);
    }
  };

  const handleDelete = async (resumeId, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this resume?')) return;
    
    try {
      await axios.delete(`http://localhost:8000/history/${resumeId}`);
      setHistory(prev => prev.filter(r => r.id !== resumeId));
    } catch (err) {
      alert('Error deleting resume');
      console.error('Error deleting resume:', err);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const toggleExpand = (id, e) => {
    e.stopPropagation();
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="history-page">
      <div className="history-header">
        <button onClick={onBack} className="back-btn">← Back to Generator</button>
        <h2>📋 Resume History</h2>
      </div>

      {loading && <p className="loading">Loading history...</p>}
      {error && <p className="error">{error}</p>}
      
      {!loading && history.length === 0 && (
        <div className="no-history">
          <p>No resumes generated yet.</p>
          <button onClick={onBack}>Generate your first resume</button>
        </div>
      )}

      <div className="history-list">
        {history.map((item) => (
          <div 
            key={item.id} 
            className={`history-item ${expandedId === item.id ? 'expanded' : ''}`}
          >
            <div className="history-item-main" onClick={() => handleSelect(item.id)}>
              <div className="history-item-info">
                <h3>{item.job_title || 'Untitled'}</h3>
                <p className="history-name">{item.name}</p>
                {item.job_link && (
                  <p className="history-link">
                    <a 
                      href={item.job_link} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                    >
                      🔗 View Job Posting
                    </a>
                  </p>
                )}
                <p className="history-date">{formatDate(item.created_at)}</p>
              </div>
              <div className="history-item-actions">
                {item.job_description && (
                  <button 
                    onClick={(e) => toggleExpand(item.id, e)}
                    className="expand-btn"
                    title="View Job Description"
                  >
                    {expandedId === item.id ? '📄 ▲' : '📄 ▼'}
                  </button>
                )}
                <button 
                  onClick={(e) => handleDelete(item.id, e)}
                  className="delete-btn"
                >
                  🗑️
                </button>
              </div>
            </div>
            {expandedId === item.id && item.job_description && (
              <div className="history-item-description" onClick={(e) => e.stopPropagation()}>
                <h4>Job Description:</h4>
                <pre>{item.job_description}</pre>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default HistoryPage;

