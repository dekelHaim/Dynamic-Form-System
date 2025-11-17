import React, { useState, useEffect, useRef } from 'react';
import formService from '../api/formService';
import '../styles/SubmissionsList.css';

const SubmissionsList = () => {
  const [submissions, setSubmissions] = useState([]);
  const [filteredSubmissions, setFilteredSubmissions] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Filter & Search State
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  
  // Sort state - tracking which field and direction
  const [sortBy, setSortBy] = useState('submitted_at'); // id, submitted_at, name, email, age, gender
  const [sortOrder, setSortOrder] = useState('desc'); // asc, desc
  
  // Debounce timer ref
  const debounceTimer = useRef(null);

  // Fetch all submissions from backend with sorting
  const fetchSubmissions = async () => {
    setLoading(true);
    setError('');
    try {
      const params = {
        skip: 0,
        limit: 1000, // Get all to enable client-side filtering
        sort_by: sortBy === 'submitted_at' ? 'submitted_at' : 'id', // Backend only supports these
        order: sortOrder,
      };
      
      const response = await formService.getSubmissions(params);
      setSubmissions(response.submissions || []);
      setTotal(response.submissions?.length || 0);
    } catch (err) {
      console.error('Error fetching submissions:', err);
      setError(`Failed to load submissions: ${err.detail || err.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle search with debounce
  const handleSearchChange = (value) => {
    setSearchQuery(value);
    setPage(0); // Reset to first page on search
    
    // Clear previous timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    
    // Set new timer - search will trigger after 500ms of no typing
    debounceTimer.current = setTimeout(() => {
      // Filter will happen in the useEffect below
    }, 500);
  };

  // Client-side sorting logic for all fields
  const sortSubmissions = (data) => {
    const sorted = [...data];
    
    sorted.sort((a, b) => {
      let aValue, bValue;
      const formDataA = a.form_data || {};
      const formDataB = b.form_data || {};

      // Get values based on sort field
      switch (sortBy) {
        case 'id':
          aValue = a.id;
          bValue = b.id;
          break;
        case 'submitted_at':
          aValue = new Date(a.submitted_at).getTime();
          bValue = new Date(b.submitted_at).getTime();
          break;
        case 'name':
          aValue = (formDataA.name || '').toLowerCase();
          bValue = (formDataB.name || '').toLowerCase();
          break;
        case 'email':
          aValue = (formDataA.email || '').toLowerCase();
          bValue = (formDataB.email || '').toLowerCase();
          break;
        case 'age':
          aValue = parseInt(formDataA.age) || 0;
          bValue = parseInt(formDataB.age) || 0;
          break;
        case 'gender':
          aValue = (formDataA.gender || '').toLowerCase();
          bValue = (formDataB.gender || '').toLowerCase();
          break;
        default:
          aValue = a.id;
          bValue = b.id;
      }

      // Compare values
      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return sorted;
  };

  // Apply filters and search
  useEffect(() => {
    let result = [...submissions];

    // Smart search - search by NAME, EMAIL, or any field
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(sub => {
        const data = sub.form_data || {};
        
        // Search in multiple fields
        return (
          (data.name && data.name.toLowerCase().includes(query)) ||
          (data.email && data.email.toLowerCase().includes(query)) ||
          (data.age && String(data.age).includes(query)) ||
          (data.gender && data.gender.toLowerCase().includes(query)) ||
          (String(sub.id).includes(query))
        );
      });
    }

    // Apply sorting on filtered results
    result = sortSubmissions(result);

    // Pagination
    const startIdx = page * pageSize;
    const paginatedResult = result.slice(startIdx, startIdx + pageSize);
    
    setFilteredSubmissions(paginatedResult);
    setTotal(result.length);
  }, [submissions, searchQuery, page, pageSize, sortBy, sortOrder]);

  // Fetch on mount and when sorting changes
  useEffect(() => {
    setPage(0);
    fetchSubmissions();
  }, []);

  // Handle delete
  const handleDelete = async (submissionId) => {
    if (!window.confirm('Are you sure you want to delete this submission?')) return;
    
    try {
      await formService.deleteSubmission(submissionId);
      fetchSubmissions();
    } catch (err) {
      console.error('Error deleting submission:', err);
      setError(`Failed to delete submission: ${err.detail || err.message}`);
    }
  };

  // Format date nicely
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Toggle sort on table header click
  const handleColumnClick = (field) => {
    if (sortBy === field) {
      // Toggle sort order if clicking same field
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      // Set new field with desc order
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  // Get sort indicator for column headers
  const getSortIndicator = (field) => {
    if (sortBy !== field) return ' ⇅';
    return sortOrder === 'asc' ? ' ↑' : ' ↓';
  };

  const totalPages = Math.ceil(total / pageSize) || 1;
  const hasNextPage = page < totalPages - 1;
  const hasPreviousPage = page > 0;

  return (
    <div className="submissions-container">
      <div className="submissions-header">
        <h2>Manage and monitor all form entries</h2>
        
        {error && <div className="error-message">{error}</div>}
        {loading && <div className="loading-message">Loading submissions...</div>}
      </div>

      <div className="search-sort-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by name, email, age, gender, or ID..."
            value={searchQuery}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="search-input"
          />
        </div>

        {/* Sort Controls */}
        <div className="sort-controls">
          <label>Sort by:</label>
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="id">ID</option>
            <option value="submitted_at">Submitted At</option>
            <option value="name">Name</option>
            <option value="email">Email</option>
            <option value="age">Age</option>
            <option value="gender">Gender</option>
          </select>

          <label>Order:</label>
          <select 
            value={sortOrder} 
            onChange={(e) => setSortOrder(e.target.value)}
            className="sort-select"
          >
            <option value="asc">Ascending (A→Z, 0→9)</option>
            <option value="desc">Descending (Z→A, 9→0)</option>
          </select>
        </div>
      </div>

      {/* Results Info */}
      <div className="results-info">
        <p>
          Showing {filteredSubmissions.length > 0 ? page * pageSize + 1 : 0} to{' '}
          {Math.min((page + 1) * pageSize, total)} of {total} submissions
        </p>
      </div>

      {/* Table */}
      <div className="table-container">
        <table className="submissions-table">
          <thead>
            <tr>
              <th 
                onClick={() => handleColumnClick('id')}
                className="clickable-header"
                title="Click to sort"
              >
                ID {getSortIndicator('id')}
              </th>
              <th 
                onClick={() => handleColumnClick('submitted_at')}
                className="clickable-header"
                title="Click to sort"
              >
                Submitted At {getSortIndicator('submitted_at')}
              </th>
              <th 
                onClick={() => handleColumnClick('name')}
                className="clickable-header"
                title="Click to sort"
              >
                Name {getSortIndicator('name')}
              </th>
              <th 
                onClick={() => handleColumnClick('email')}
                className="clickable-header"
                title="Click to sort"
              >
                Email {getSortIndicator('email')}
              </th>
              <th 
                onClick={() => handleColumnClick('age')}
                className="clickable-header"
                title="Click to sort"
              >
                Age {getSortIndicator('age')}
              </th>
              <th 
                onClick={() => handleColumnClick('gender')}
                className="clickable-header"
                title="Click to sort"
              >
                Gender {getSortIndicator('gender')}
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredSubmissions.length > 0 ? (
              filteredSubmissions.map((submission) => {
                const data = submission.form_data || {};
                return (
                  <tr key={submission.id} className="submission-row">
                    <td>#{submission.id}</td>
                    <td>{formatDate(submission.submitted_at)}</td>
                    <td>{data.name || '-'}</td>
                    <td>{data.email || '-'}</td>
                    <td>{data.age || '-'}</td>
                    <td className="gender-cell">
                      {data.gender ? (
                        <span className={`gender-badge gender-${data.gender.toLowerCase()}`}>
                          {data.gender}
                        </span>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td className="actions-cell">
                      <button
                        onClick={() => handleDelete(submission.id)}
                        className="delete-btn"
                        title="Delete submission"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="7" className="empty-message">
                  {searchQuery ? 'No submissions match your search' : 'No submissions yet'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="pagination-controls">
        <button
          onClick={() => setPage(Math.max(0, page - 1))}
          disabled={!hasPreviousPage}
          className="pagination-btn"
        >
          ← Previous
        </button>

        <span className="page-indicator">
          Page {page + 1} of {totalPages}
        </span>

        <button
          onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
          disabled={!hasNextPage}
          className="pagination-btn"
        >
          Next →
        </button>

        <select
          value={pageSize}
          onChange={(e) => {
            setPageSize(parseInt(e.target.value));
            setPage(0);
          }}
          className="page-size-select"
        >
          <option value={5}>5 per page</option>
          <option value={10}>10 per page</option>
          <option value={20}>20 per page</option>
          <option value={50}>50 per page</option>
        </select>
      </div>
    </div>
  );
};

export default SubmissionsList;