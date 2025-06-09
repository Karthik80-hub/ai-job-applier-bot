import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await fetch('/api/jobs');
      if (!response.ok) {
        throw new Error('Failed to fetch jobs');
      }
      const data = await response.json();
      setJobs(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleApply = async (job) => {
    try {
      const response = await fetch(`/api/jobs/${job.url}/apply`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to apply to job');
      }
      
      const result = await response.json();
      
      // Update job status in the list
      setJobs(jobs.map(j => 
        j.url === job.url 
          ? { ...j, status: 'applying' }
          : j
      ));
      
      // Show success notification
      setNotification({
        type: 'success',
        message: 'Application process started successfully!'
      });
      
      // Clear notification after 5 seconds
      setTimeout(() => setNotification(null), 5000);
      
    } catch (err) {
      setNotification({
        type: 'error',
        message: err.message
      });
      setTimeout(() => setNotification(null), 5000);
    }
  };

  const MatchScore = ({ score }) => (
    <div className="w-full mt-2">
      <div className="flex justify-between mb-1">
        <span className="text-sm font-medium">ATS Match Score</span>
        <span className="text-sm font-medium">{score}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-blue-600 h-2 rounded-full" 
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );

  const Notification = ({ type, message }) => (
    <div className={`fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg ${
      type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white`}>
      {message}
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>Error: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4 sm:px-6 lg:px-8">
      {notification && (
        <Notification type={notification.type} message={notification.message} />
      )}
      
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">AI Job Matcher Dashboard</h1>
          <p className="mt-2 text-gray-600">Found {jobs.length} matched positions for your profile</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {jobs.map((job, index) => (
            <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
              <div className="p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-2">{job.title}</h2>
                <p className="text-gray-600 mb-4">{job.company} • {job.location}</p>
                
                <MatchScore score={job.match_score} />

                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-900">Matched Skills</h3>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {job.matched_skills.map((skill, idx) => (
                      <span 
                        key={idx}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-6 flex gap-4">
                  <button 
                    onClick={() => window.open(job.url, '_blank')}
                    className="flex-1 bg-white border border-blue-600 text-blue-600 px-4 py-2 rounded-md hover:bg-blue-50 transition-colors duration-300"
                  >
                    Preview
                  </button>
                  <button 
                    onClick={() => handleApply(job)}
                    disabled={job.status === 'applying'}
                    className={`flex-1 px-4 py-2 rounded-md transition-colors duration-300 ${
                      job.status === 'applying'
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 hover:bg-blue-700 text-white'
                    }`}
                  >
                    {job.status === 'applying' ? 'Applying...' : 'Apply Now'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
