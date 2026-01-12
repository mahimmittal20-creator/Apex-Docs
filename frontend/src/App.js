import React, { useState } from 'react';
import './App.css';
import RawResumeInputForm from './components/RawResumeInputForm';
import ResumeDisplay from './components/ResumeDisplay';
import ChatBox from './components/ChatBox';
import HistoryPage from './components/HistoryPage';

function App() {
  const [currentResumeId, setCurrentResumeId] = useState(''); 
  const [currentJobTitleForDownload, setCurrentJobTitleForDownload] = useState(''); 
  const [displayedResume, setDisplayedResume] = useState(null);
  const [currentPage, setCurrentPage] = useState('generator'); // 'generator' or 'history'

  const handleResumeGenerated = (resumeId, jobTitleForDownload, resumeData) => {
    setCurrentResumeId(resumeId); 
    setCurrentJobTitleForDownload(jobTitleForDownload); 
    setDisplayedResume(resumeData);
  };

  const handleSelectFromHistory = (resumeId, jobTitle, resumeData) => {
    setCurrentResumeId(resumeId);
    setCurrentJobTitleForDownload(jobTitle);
    setDisplayedResume(resumeData);
    setCurrentPage('generator');
  };

  if (currentPage === 'history') {
    return (
      <div className="App">
        <HistoryPage 
          onSelectResume={handleSelectFromHistory}
          onBack={() => setCurrentPage('generator')}
        />
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>AI Resume Tailor</h1>
        <button 
          onClick={() => setCurrentPage('history')} 
          className="history-btn"
        >
          📋 History
        </button>
      </header>
      
      <hr />
      
      <div className="main-content">
        <div className="left-panel">
          <RawResumeInputForm onResumeGenerated={handleResumeGenerated} />
        </div>
        
        <div className="right-panel">
          <ResumeDisplay 
            resumeId={currentResumeId}
            jobTitleForDownload={currentJobTitleForDownload}
            generatedResume={displayedResume}
            setGeneratedResume={setDisplayedResume} 
          />
          
          <hr />
          
          <ChatBox resumeId={currentResumeId} />
        </div>
      </div>
    </div>
  );
}

export default App;
