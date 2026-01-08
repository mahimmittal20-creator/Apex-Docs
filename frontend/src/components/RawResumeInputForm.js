import React, { useState } from 'react';
import axios from 'axios';

function RawResumeInputForm({ onResumeGenerated }) {
  const [jobDescriptionText, setJobDescriptionText] = useState('');
  const [desiredFilenameJobTitle, setDesiredFilenameJobTitle] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/generate_tailored_resume/', {
        job_description_text: jobDescriptionText,
        desired_filename_job_title: desiredFilenameJobTitle,
      });
      console.log('Tailored Resume Generated:', response.data);
      alert('Tailored Resume Generated Successfully!');
      if (onResumeGenerated) {
        onResumeGenerated(
          response.data.resume_id,
          desiredFilenameJobTitle,
          response.data.resume_data
        );
      }
      setJobDescriptionText('');
    } catch (error) {
      console.error('Error generating tailored resume:', error);
      alert('Error generating tailored resume. Please ensure your OpenAI API key is configured correctly in the backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Generate Tailored Resume</h2>
      <div>
        <label>Paste the Job Description:</label>
        <textarea
          value={jobDescriptionText}
          onChange={(e) => setJobDescriptionText(e.target.value)}
          rows="20"
          placeholder="Paste the full job description here..."
          required
        />
      </div>
      <div>
        <label>Job Title for Download Filename:</label>
        <input 
          type="text" 
          value={desiredFilenameJobTitle} 
          onChange={(e) => setDesiredFilenameJobTitle(e.target.value)} 
          placeholder="e.g., Software Engineer" 
          required 
        />
      </div>
      <button type="submit" disabled={loading}>
        {loading ? 'Generating...' : 'Generate Tailored Resume'}
      </button>
      {loading && <p>This might take a moment as AI processes your resume.</p>}
    </form>
  );
}

export default RawResumeInputForm;

