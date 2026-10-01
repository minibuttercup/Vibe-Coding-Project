/**
 * Loans API Functions
 * 
 * Provides functions for loan application operations:
 * - createApplication: Create new loan application
 * - getMyApplication: Get current user's application
 * - updateApplication: Update loan application
 * - deleteApplication: Delete loan application
 * - submitApplication: Submit for decision
 */

import api from './client';

// =====================================================
// TYPES
// =====================================================
export interface PersonalInfo {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
}

export interface LoanDetails {
  amount: number;
  term: number;
  purpose?: string;
}

export interface CreateApplicationData {
  personal_info: PersonalInfo;
  loan_details?: LoanDetails;
}

export interface UpdateApplicationData {
  personal_info?: PersonalInfo;
  loan_details?: LoanDetails;
}

export interface ApplicationResponse {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  loan_amount?: number;
  loan_term?: number;
  loan_purpose?: string;
  created_at?: string;
  updated_at?: string;
}

export interface DecisionResult {
  approved: boolean;
  reason: string;
}

export interface SubmitResponse {
  application: ApplicationResponse;
  decision: DecisionResult;
}

// =====================================================
// API FUNCTIONS
// =====================================================

/**
 * Create a new loan application
 */
export async function createApplication(data: CreateApplicationData): Promise<ApplicationResponse> {
  return api.post<ApplicationResponse>('/loans', data);
}

/**
 * Get current user's loan application
 */
export async function getMyApplication(): Promise<ApplicationResponse | null> {
  try {
    return await api.get<ApplicationResponse | null>('/loans/me');
  } catch {
    return null;
  }
}

/**
 * Update a loan application
 */
export async function updateApplication(
  applicationId: string,
  data: UpdateApplicationData
): Promise<ApplicationResponse> {
  return api.put<ApplicationResponse>(`/loans/${applicationId}`, data);
}

/**
 * Delete a loan application
 */
export async function deleteApplication(applicationId: string): Promise<void> {
  await api.delete(`/loans/${applicationId}`);
}

/**
 * Submit application for decision
 */
export async function submitApplication(applicationId: string): Promise<SubmitResponse> {
  return api.post<SubmitResponse>(`/loans/${applicationId}/submit`, {});
}