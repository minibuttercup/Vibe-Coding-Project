/**
 * App.tsx - Central state management and routing
 * 
 * ============================================
 * HOW DATA FLOWS IN THIS APPLICATION
 * ============================================
 * 
 * 1. PROPS DOWN (App → Pages):
 *    - App stores all form data in state
 *    - App passes saved data to each page via props
 *    - Pages receive data and use it to initialize their local form state
 * 
 * 2. CALLBACKS UP (Pages → App):
 *    - Each page has an `onComplete` callback prop
 *    - When user clicks "Next", page validates and calls onComplete(data)
 *    - App receives the data and updates its central state
 * 
 * 3. ROUTER STATE (Summary → Decision):
 *    - On submit, App navigates to /decision with state object
 *    - DecisionPage reads the decision result from useLocation().state
 *    - This demonstrates one-time data transfer via router
 * 
 * ============================================
 * BACKEND INTEGRATION
 * ============================================
 * 
 * - AuthProvider wraps the app for authentication state
 * - API calls are made to the FastAPI backend
 * - Decision logic is now handled by the backend
 */

import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import { useState, useCallback } from 'react';
import type { PersonalInfo, LoanDetails, LoanApplication, DecisionResult } from './types';
import { AuthProvider } from './context/AuthContext';
import { LandingPage } from './pages/LandingPage';
import { PersonalInfoPage } from './pages/PersonalInfoPage';
import { LoanDetailsPage } from './pages/LoanDetailsPage';
import { SummarySubmitPage } from './pages/SummarySubmitPage';
import { DecisionPage } from './pages/DecisionPage';
import { createApplication, updateApplication, submitApplication } from './api/loans';

// Default empty state for a new application
const defaultApplication: LoanApplication = {
  personalInfo: {
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
  },
  loanDetails: {
    amount: 0,
    term: 0,
    purpose: '',
  },
};

/**
 * LoanApp component - contains all the routing logic
 * We need this as a separate component so we can use useNavigate
 */
function LoanApp() {
  // ============================================
  // CENTRAL STATE - All form data stored here
  // ============================================
  const [application, setApplication] = useState<LoanApplication>(() => {
    // Try to load from localStorage on initial mount
    const saved = localStorage.getItem('loanApplication');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        // Only restore if it has the expected structure
        if (parsed.personalInfo && parsed.loanDetails) {
          return parsed;
        }
      } catch {
        // If parsing fails, use default
      }
    }
    return defaultApplication;
  });

  const [applicationId, setApplicationId] = useState<string | null>(null);
  const navigate = useNavigate();

  // ============================================
  // CALLBACK FUNCTIONS - Pages call these to update App state
  // ============================================

  /**
   * Called by PersonalInfoPage when user clicks "Next"
   * Updates personalInfo in central state and navigates to next page
   */
  const handlePersonalInfoComplete = useCallback(async (data: PersonalInfo) => {
    setApplication(prev => ({
      ...prev,
      personalInfo: data,
    }));
    
    // Save to backend - create or update application
    try {
      if (!applicationId) {
        const response = await createApplication({
          personal_info: {
            first_name: data.firstName,
            last_name: data.lastName,
            email: data.email,
            phone: data.phone,
          },
        });
        setApplicationId(response.id);
      } else {
        await updateApplication(applicationId, {
          personal_info: {
            first_name: data.firstName,
            last_name: data.lastName,
            email: data.email,
            phone: data.phone,
          },
        });
      }
    } catch (error) {
      console.error('Failed to save personal info:', error);
    }
    
    navigate('/loan-details');
  }, [navigate, applicationId]);

  /**
   * Called by LoanDetailsPage when user clicks "Next"
   * Updates loanDetails in central state and navigates to summary
   */
  const handleLoanDetailsComplete = useCallback(async (data: LoanDetails) => {
    setApplication(prev => ({
      ...prev,
      loanDetails: data,
    }));
    
    // Save to backend
    try {
      if (applicationId) {
        await updateApplication(applicationId, {
          loan_details: {
            amount: data.amount,
            term: data.term,
            purpose: data.purpose,
          },
        });
      }
    } catch (error) {
      console.error('Failed to save loan details:', error);
    }
    
    navigate('/summary');
  }, [navigate, applicationId]);

  /**
   * Called by SummarySubmitPage when user clicks "Submit Application"
   * Calls backend API to submit application and get decision
   */
  const handleSubmitApplication = useCallback(async () => {
    if (!applicationId) {
      console.error('No application ID');
      return;
    }

    try {
      const response = await submitApplication(applicationId);
      const decision: DecisionResult = {
        approved: response.decision.approved,
        reason: response.decision.reason,
      };

      // Save complete application with decision to localStorage
      localStorage.setItem('loanApplication', JSON.stringify({
        ...application,
        decision,
        submittedAt: new Date().toISOString(),
      }));

      // Navigate to decision page with router state
      navigate('/decision', { state: decision });
    } catch (error) {
      console.error('Failed to submit application:', error);
    }
  }, [application, applicationId, navigate]);

  /**
   * Called to reset the application and start fresh
   */
  const handleStartNew = useCallback(() => {
    setApplication(defaultApplication);
    setApplicationId(null);
    localStorage.removeItem('loanApplication');
    navigate('/apply');
  }, [navigate]);

  // ============================================
  // ROUTING - Each route renders a page with props
  // ============================================
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Landing Page */}
        <Route path="/" element={<LandingPage />} />

        {/* Page 1: Personal Information */}
        <Route
          path="/apply"
          element={
            <PersonalInfoPage
              initialData={application.personalInfo}
              onComplete={handlePersonalInfoComplete}
            />
          }
        />

        {/* Page 2: Loan Details */}
        <Route
          path="/loan-details"
          element={
            <LoanDetailsPage
              initialData={application.loanDetails}
              onComplete={handleLoanDetailsComplete}
            />
          }
        />

        {/* Page 3: Summary & Submit */}
        <Route
          path="/summary"
          element={
            <SummarySubmitPage
              personalInfo={application.personalInfo}
              loanDetails={application.loanDetails}
              onSubmit={handleSubmitApplication}
            />
          }
        />

        {/* Page 4: Decision Result */}
        <Route
          path="/decision"
          element={
            <DecisionPage onStartNew={handleStartNew} />
          }
        />
      </Routes>
    </div>
  );
}

/**
 * App component - wraps everything in BrowserRouter and AuthProvider
 */
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <LoanApp />
      </AuthProvider>
    </BrowserRouter>
  );
}