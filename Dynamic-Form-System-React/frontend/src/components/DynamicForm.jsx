import React, { useState, useEffect } from 'react';
import formService from '../api/formService';
import '../styles/DynamicForm.css';

/**
 * DynamicForm Component - Renders form fields based on JSON schema
 * @param {Object} schema - JSON schema defining form fields
 * @param {Function} onSuccess - Callback after successful submission
 */
const DynamicForm = ({ schema, onSuccess }) => {
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');
  const [submitError, setSubmitError] = useState('');
  const [existingEmails, setExistingEmails] = useState([]);

  // Initialize form data and load existing emails on component mount
  useEffect(() => {
    const initialData = {};
    Object.keys(schema).forEach(key => {
      initialData[key] = '';
    });
    setFormData(initialData);
    
    // Load existing emails from backend
    loadExistingEmails();
  }, [schema]);

  /**
   * Load all existing emails from database
   */
  const loadExistingEmails = async () => {
    try {
      const response = await formService.getSubmissions({ limit: 1000, skip: 0 });
      const emails = response.submissions
        .map(s => s.form_data.email)
        .filter(email => email); // Remove empty emails
      setExistingEmails([...new Set(emails)]); // Remove duplicates
    } catch (error) {
      console.error('Error loading existing emails:', error);
    }
  };

  /**
   * Handle input change
   */
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  /**
   * Validate form data based on schema
   */
  const validateForm = () => {
    const newErrors = {};

    Object.entries(schema).forEach(([fieldName, fieldConfig]) => {
      const value = formData[fieldName];
      const fieldErrors = [];

      // Check required
      if (fieldConfig.required && (value === '' || value === null || value === undefined)) {
        fieldErrors.push(`${fieldName} is required`);
      }

      if (value === '' || value === null || value === undefined) {
        if (fieldErrors.length > 0) {
          newErrors[fieldName] = fieldErrors;
        }
        return;
      }

      // Validate by type
      if (fieldConfig.type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
          fieldErrors.push('Invalid email format');
        }
        
        // Check if email already exists
        if (existingEmails.includes(value)) {
          fieldErrors.push('⚠️ This email already exists in the system. Please use a different email.');
        }
      }

      if (fieldConfig.type === 'string' || fieldConfig.type === 'text') {
        if (fieldConfig.minLength && value.length < fieldConfig.minLength) {
          fieldErrors.push(`Must be at least ${fieldConfig.minLength} characters`);
        }
        if (fieldConfig.maxLength && value.length > fieldConfig.maxLength) {
          fieldErrors.push(`Must be at most ${fieldConfig.maxLength} characters`);
        }
      }

      if (fieldConfig.type === 'number') {
        const numValue = parseFloat(value);
        if (isNaN(numValue)) {
          fieldErrors.push('Must be a valid number');
        } else {
          if (fieldConfig.min !== undefined && numValue < fieldConfig.min) {
            fieldErrors.push(`Must be at least ${fieldConfig.min}`);
          }
          if (fieldConfig.max !== undefined && numValue > fieldConfig.max) {
            fieldErrors.push(`Must be at most ${fieldConfig.max}`);
          }
        }
      }

      if (fieldConfig.type === 'date') {
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(value)) {
          fieldErrors.push('Invalid date format (use YYYY-MM-DD)');
        }
      }

      if (fieldConfig.type === 'dropdown') {
        if (!fieldConfig.options || !fieldConfig.options.includes(value)) {
          fieldErrors.push('Invalid selection');
        }
      }

      if (fieldErrors.length > 0) {
        newErrors[fieldName] = fieldErrors;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitMessage('');
    setSubmitError('');

    // Validate
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const response = await formService.submitForm(formData);
      
      setSubmitMessage(`✅ Form submitted successfully! (ID: ${response.id}${response.is_duplicate ? ' - Duplicate detected' : ''})`);
      setFormData({});
      setErrors({});
      
      // Reload existing emails after successful submission
      loadExistingEmails();
      
      if (onSuccess) {
        onSuccess(response);
      }

      // Clear message after 5 seconds
      setTimeout(() => setSubmitMessage(''), 5000);
    } catch (error) {
      console.error('Submission error:', error);
      
      // Check if error is about duplicate email
      const errorDetail = error.detail || error.message || 'Unknown error';
      if (errorDetail.includes('already exists')) {
        setSubmitError(`❌ ${errorDetail}`);
      } else {
        setSubmitError(`❌ Error submitting form: ${errorDetail}`);
      }
      
      // Clear error after 5 seconds
      setTimeout(() => setSubmitError(''), 5000);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Render form field based on type
   */
  const renderField = (fieldName, fieldConfig) => {
    const value = formData[fieldName] || '';
    const fieldErrors = errors[fieldName] || [];
    const isEmailDuplicate = fieldName === 'email' && value && existingEmails.includes(value);

    switch (fieldConfig.type) {
      case 'text':
      case 'string':
        return (
          <div key={fieldName} className="form-group">
            <label htmlFor={fieldName}>
              {fieldName}
              {fieldConfig.required && <span className="required">*</span>}
            </label>
            <input
              type="text"
              id={fieldName}
              name={fieldName}
              value={value}
              onChange={handleChange}
              placeholder={`Enter ${fieldName}`}
              className={fieldErrors.length > 0 ? 'input-error' : ''}
            />
            {fieldErrors.map((error, idx) => (
              <span key={idx} className="error-message">{error}</span>
            ))}
          </div>
        );

      case 'email':
        return (
          <div key={fieldName} className="form-group">
            <label htmlFor={fieldName}>
              {fieldName}
              {fieldConfig.required && <span className="required">*</span>}
              {isEmailDuplicate && <span className="warning-icon"> ⚠️</span>}
            </label>
            <input
              type="email"
              id={fieldName}
              name={fieldName}
              value={value}
              onChange={handleChange}
              placeholder={`Enter ${fieldName}`}
              className={fieldErrors.length > 0 || isEmailDuplicate ? 'input-error' : ''}
            />
            {fieldErrors.map((error, idx) => (
              <span key={idx} className="error-message">{error}</span>
            ))}
          </div>
        );

      case 'password':
        return (
          <div key={fieldName} className="form-group">
            <label htmlFor={fieldName}>
              {fieldName}
              {fieldConfig.required && <span className="required">*</span>}
            </label>
            <input
              type="password"
              id={fieldName}
              name={fieldName}
              value={value}
              onChange={handleChange}
              placeholder={`Enter ${fieldName}`}
              className={fieldErrors.length > 0 ? 'input-error' : ''}
            />
            {fieldErrors.map((error, idx) => (
              <span key={idx} className="error-message">{error}</span>
            ))}
          </div>
        );

      case 'number':
        return (
          <div key={fieldName} className="form-group">
            <label htmlFor={fieldName}>
              {fieldName}
              {fieldConfig.required && <span className="required">*</span>}
            </label>
            <input
              type="number"
              id={fieldName}
              name={fieldName}
              value={value}
              onChange={handleChange}
              placeholder={`Enter ${fieldName}`}
              className={fieldErrors.length > 0 ? 'input-error' : ''}
            />
            {fieldErrors.map((error, idx) => (
              <span key={idx} className="error-message">{error}</span>
            ))}
          </div>
        );

      case 'date':
        return (
          <div key={fieldName} className="form-group">
            <label htmlFor={fieldName}>
              {fieldName}
              {fieldConfig.required && <span className="required">*</span>}
            </label>
            <input
              type="date"
              id={fieldName}
              name={fieldName}
              value={value}
              onChange={handleChange}
              className={fieldErrors.length > 0 ? 'input-error' : ''}
            />
            {fieldErrors.map((error, idx) => (
              <span key={idx} className="error-message">{error}</span>
            ))}
          </div>
        );

      case 'dropdown':
        return (
          <div key={fieldName} className="form-group">
            <label htmlFor={fieldName}>
              {fieldName}
              {fieldConfig.required && <span className="required">*</span>}
            </label>
            <select
              id={fieldName}
              name={fieldName}
              value={value}
              onChange={handleChange}
              className={fieldErrors.length > 0 ? 'input-error' : ''}
            >
              <option value="">-- Select {fieldName} --</option>
              {fieldConfig.options && fieldConfig.options.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
            {fieldErrors.map((error, idx) => (
              <span key={idx} className="error-message">{error}</span>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="dynamic-form">
      <h2>Form Submission</h2>

      {submitMessage && <div className="success-message">{submitMessage}</div>}
      {submitError && <div className="error-alert">{submitError}</div>}

      {Object.entries(schema).map(([fieldName, fieldConfig]) =>
        renderField(fieldName, fieldConfig)
      )}

      <button type="submit" disabled={loading} className="submit-btn">
        {loading ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
};

export default DynamicForm;