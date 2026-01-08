import React, { useState } from 'react';
import './App.css';
import RawResumeInputForm from './components/RawResumeInputForm';
import ResumeDisplay from './components/ResumeDisplay';

function App() {
  const [currentResumeId, setCurrentResumeId] = useState(''); 
  const [currentJobTitleForDownload, setCurrentJobTitleForDownload] = useState(''); 
  const [displayedResume, setDisplayedResume] = useState(null);

  const handleResumeGenerated = (resumeId, jobTitleForDownload, resumeData) => {
    setCurrentResumeId(resumeId); 
    setCurrentJobTitleForDownload(jobTitleForDownload); 
    setDisplayedResume(resumeData);
  };

  return (
    <div className="App">
      <h1>AI Resume Tailor</h1>
      <hr />
      <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap' }}>
        <RawResumeInputForm onResumeGenerated={handleResumeGenerated} />
      </div>
      <hr />
      <ResumeDisplay 
        resumeId={currentResumeId}
        jobTitleForDownload={currentJobTitleForDownload}
        generatedResume={displayedResume}
        setGeneratedResume={setDisplayedResume} 
      />
    </div>
  );
}

export default App;
