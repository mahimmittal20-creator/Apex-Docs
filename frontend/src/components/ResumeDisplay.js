import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ResumeDisplay({ resumeId: propResumeId, jobTitleForDownload: propJobTitleForDownload, generatedResume: propGeneratedResume }) {
  const [generatedResume, setGeneratedResume] = useState(propGeneratedResume);
  const [currentResumeId, setCurrentResumeId] = useState(propResumeId);
  const [currentJobTitleForDownload, setCurrentJobTitleForDownload] = useState(propJobTitleForDownload);

  useEffect(() => {
    setGeneratedResume(propGeneratedResume);
    setCurrentResumeId(propResumeId);
    setCurrentJobTitleForDownload(propJobTitleForDownload);
  }, [propGeneratedResume, propResumeId, propJobTitleForDownload]);

  const handleDownload = async (format) => {
    if (!generatedResume || !currentResumeId || !currentJobTitleForDownload) {
      alert("Please generate a resume first before downloading.");
      return;
    }
    try {
      const response = await axios.get(`http://localhost:8000/download_resume/${format}/${currentResumeId}/${currentJobTitleForDownload}/`, {
        responseType: 'blob', // Important for downloading files
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      // Use .docx extension for Word files, .pdf for PDF
      const fileExtension = format === 'word' ? 'docx' : format;
      link.setAttribute('download', `${generatedResume.name.replace(' ', '_')}_${currentJobTitleForDownload}_resume.${fileExtension}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      alert(`Resume downloaded as ${format === 'word' ? 'DOCX' : format.toUpperCase()}!`);
    } catch (error) {
      console.error(`Error downloading ${format} resume:`, error);
      alert(`Error downloading ${format} resume. Ensure a resume is generated.`);
    }
  };

  return (
    <div className="ResumeDisplay">
      <h2>Tailored Resume</h2>
      
      {generatedResume ? (
        <div>
          <h3>Generated Resume for {generatedResume.name}</h3>
          <p>Email: {generatedResume.email}</p>
          {generatedResume.phone && <p>Phone: {generatedResume.phone}</p>}
          {generatedResume.location && <p>Location: {generatedResume.location}</p>}
          {generatedResume.linkedin && <p>LinkedIn: <a href={generatedResume.linkedin} target="_blank" rel="noopener noreferrer">{generatedResume.linkedin}</a></p>}
          {generatedResume.github && <p>GitHub: <a href={generatedResume.github} target="_blank" rel="noopener noreferrer">{generatedResume.github}</a></p>}
          <p>Summary: {generatedResume.summary}</p>
          <p>Skills: {generatedResume.skills.join(', ')}</p>
          <h4>Experience:</h4>
          {generatedResume.experience.map((exp, index) => (
            <div key={index}>
              <p>  - <strong>{exp.title}</strong> at {exp.company} ({exp.start_date} - {exp.end_date || 'Present'})</p>
              <p>    {exp.description}</p>
            </div>
          ))}
          <h4>Education:</h4>
          {generatedResume.education.map((edu, index) => (
            <div key={index}>
              <p>  - {edu.degree} in {edu.major} from {edu.university} ({edu.graduation_date})</p>
            </div>
          ))}
          {generatedResume.projects && generatedResume.projects.length > 0 && <h4>Projects:</h4>}
          {generatedResume.projects && generatedResume.projects.length > 0 && <p>{generatedResume.projects.join(', ')}</p>}
          {generatedResume.certifications && generatedResume.certifications.length > 0 && <h4>Certifications:</h4>}
          {generatedResume.certifications && generatedResume.certifications.length > 0 && <p>{generatedResume.certifications.join(', ')}</p>}
          <hr />
          <button onClick={() => handleDownload('pdf')}>Download as PDF</button>
          <button onClick={() => handleDownload('word')}>Download as Word</button>
        </div>
      ) : (
        <p>Your tailored resume will appear here after generation.</p>
      )}
    </div>
  );
}

export default ResumeDisplay;

