import React, { useState } from 'react';
import DynamicForm from './components/DynamicForm';
import SubmissionsList from './components/SubmissionsList';
import './styles/App.css';

/**
 * Main App Component
 */
const App = () => {
  const [activeTab, setActiveTab] = useState('form');
  const [refreshSubmissions, setRefreshSubmissions] = useState(0);

  // Example form schema - matches backend requirements
  const formSchema = {
    name: {
      type: 'string',
      required: true,
      minLength: 3,
      maxLength: 50,
    },
    email: {
      type: 'email',
      required: true,
    },
    age: {
      type: 'number',
      required: true,
      min: 0,
      max: 120,
    },
    gender: {
      type: 'dropdown',
      required: true,
      options: ['male', 'female', 'other'],
    },
  };

  /**
   * Handle successful form submission
   */
  const handleFormSuccess = (response) => {
    console.log('Form submitted successfully:', response);
    // Refresh submissions list
    setRefreshSubmissions(prev => prev + 1);
    // Switch to submissions tab
    setActiveTab('submissions');
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <h1>Dynamic Form System</h1>
        <p>Submit forms, view submissions, detect duplicates</p>
      </header>

      {/* Navigation Tabs */}
      <nav className="app-nav">
        <button
          className={`tab-btn ${activeTab === 'form' ? 'active' : ''}`}
          onClick={() => setActiveTab('form')}
        >
          📋 Submit Form
        </button>
        <button
          className={`tab-btn ${activeTab === 'submissions' ? 'active' : ''}`}
          onClick={() => setActiveTab('submissions')}
        >
          📊 View Submissions
        </button>
      </nav>

      {/* Main Content */}
      <main className="app-main">
        <div className="container">
          {activeTab === 'form' && (
            <section className="tab-content">
              <DynamicForm schema={formSchema} onSuccess={handleFormSuccess} />
            </section>
          )}

          {activeTab === 'submissions' && (
            <section className="tab-content">
              <SubmissionsList key={refreshSubmissions} />
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>© 2025 Dynamic Form System | API Status: Connected</p>
      </footer>
    </div>
  );
};

export default App;