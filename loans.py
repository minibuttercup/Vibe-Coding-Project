"""
Loan Application Endpoints

This module provides API endpoints for managing loan applications.
Includes the loan decision logic moved from the frontend.

DECISION LOGIC:
- Amount > $20,000 → Requires manual review
- Amount ≤ $5,000 AND term ≤ 24 months → Approved
- Amount ≤ $20,000 AND email ends with .edu → Approved
- Otherwise → Declined
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from decimal import Decimal
import crud
from auth import get_current_user

# =====================================================
# ROUTER
# =====================================================
router = APIRouter(prefix="/loans", tags=["Loan Applications"])

# =====================================================
# REQUEST/RESPONSE MODELS
# =====================================================
class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None

class LoanDetails(BaseModel):
    amount: float
    term: int
    purpose: Optional[str] = None

class CreateApplicationRequest(BaseModel):
    personal_info: PersonalInfo
    loan_details: Optional[LoanDetails] = None

class UpdateApplicationRequest(BaseModel):
    personal_info: Optional[PersonalInfo] = None
    loan_details: Optional[LoanDetails] = None

class ApplicationResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    loan_amount: Optional[float] = None
    loan_term: Optional[int] = None
    loan_purpose: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class DecisionResult(BaseModel):
    approved: bool
    reason: str

class SubmitResponse(BaseModel):
    application: ApplicationResponse
    decision: DecisionResult

# =====================================================
# HELPER: Extract user ID from authorization header
# =====================================================
async def get_user_id_from_token(authorization: str) -> str:
    """
    Extract user ID from Authorization header.
    
    In production, you should verify the JWT signature.
    For this learning backend, we accept the token and get user info from Supabase.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    # Get user info from Supabase
    user_response = await get_current_user(authorization)
    return user_response.id

# =====================================================
# DECISION LOGIC
# =====================================================
def evaluate_loan_decision(email: str, amount: float, term: int) -> DecisionResult:
    """
    Evaluate loan application and return decision.
    
    Rules:
    1. Amount > $20,000 → Requires manual review (rejected by auto-system)
    2. Amount ≤ $5,000 AND term ≤ 24 months → Approved
    3. Amount ≤ $20,000 AND email ends with .edu → Approved
    4. Otherwise → Declined
    """
    # Rule 1: Maximum cap - amounts above $20,000 always require manual review
    if amount > 20000:
        return DecisionResult(
            approved=False,
            reason="Loan amounts above $20,000 require manual review regardless of eligibility."
        )
    
    # Rule 2: Small loans (≤ $5,000) with reasonable term
    if amount <= 5000 and term <= 24:
        return DecisionResult(
            approved=True,
            reason="Approved: Loan amount and term within acceptable limits"
        )
    
    # Rule 3: Medium loans ($5,001-$20,000) require stronger signals
    if amount <= 20000 and email.endswith('.edu'):
        return DecisionResult(
            approved=True,
            reason="Approved: Educational email address detected"
        )
    
    # Otherwise reject
    return DecisionResult(
        approved=False,
        reason="Declined: Loan amount or term exceeds our current limits"
    )

# =====================================================
# ENDPOINTS
# =====================================================

@router.post("", response_model=ApplicationResponse)
async def create_application(
    request: CreateApplicationRequest,
    authorization: str = Header(...)
):
    """
    Create a new loan application.
    
    Creates a new application with personal info and optional loan details.
    The user must be authenticated.
    """
    user_id = await get_user_id_from_token(authorization)
    
    # Extract loan details if provided
    loan_amount = None
    loan_term = None
    loan_purpose = None
    
    if request.loan_details:
        loan_amount = Decimal(str(request.loan_details.amount))
        loan_term = request.loan_details.term
        loan_purpose = request.loan_details.purpose
    
    try:
        application = crud.create_loan_application(
            user_id=user_id,
            first_name=request.personal_info.first_name,
            last_name=request.personal_info.last_name,
            email=request.personal_info.email,
            phone=request.personal_info.phone,
            loan_amount=loan_amount,
            loan_term=loan_term,
            loan_purpose=loan_purpose
        )
        return ApplicationResponse(**application)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=Optional[ApplicationResponse])
async def get_my_application(authorization: str = Header(...)):
    """
    Get the current user's loan application.
    
    Returns the user's application if it exists, or None.
    """
    user_id = await get_user_id_from_token(authorization)
    
    application = crud.get_user_application(user_id)
    if not application:
        return None
    
    return ApplicationResponse(**application)


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    request: UpdateApplicationRequest,
    authorization: str = Header(...)
):
    """
    Update a loan application.
    
    Updates personal info and/or loan details.
    Only provided fields will be updated.
    """
    user_id = await get_user_id_from_token(authorization)
    
    # Extract personal info if provided
    first_name = None
    last_name = None
    email = None
    phone = None
    
    if request.personal_info:
        first_name = request.personal_info.first_name
        last_name = request.personal_info.last_name
        email = request.personal_info.email
        phone = request.personal_info.phone
    
    # Extract loan details if provided
    loan_amount = None
    loan_term = None
    loan_purpose = None
    
    if request.loan_details:
        loan_amount = Decimal(str(request.loan_details.amount))
        loan_term = request.loan_details.term
        loan_purpose = request.loan_details.purpose
    
    try:
        application = crud.update_loan_application(
            user_id=user_id,
            application_id=application_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            loan_amount=loan_amount,
            loan_term=loan_term,
            loan_purpose=loan_purpose
        )
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        return ApplicationResponse(**application)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{application_id}")
async def delete_application(
    application_id: str,
    authorization: str = Header(...)
):
    """
    Delete a loan application.
    
    Permanently removes the application from the database.
    """
    user_id = await get_user_id_from_token(authorization)
    
    deleted = crud.delete_loan_application(user_id, application_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {"message": "Application deleted successfully"}


@router.post("/{application_id}/submit", response_model=SubmitResponse)
async def submit_application(
    application_id: str,
    authorization: str = Header(...)
):
    """
    Submit a loan application for decision.
    
    Runs the decision logic and returns the result along with
    the application data.
    """
    user_id = await get_user_id_from_token(authorization)
    
    # Get the application
    application = crud.get_loan_application(user_id, application_id)
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Validate that loan details are complete
    if not application.get("loan_amount") or not application.get("loan_term"):
        raise HTTPException(
            status_code=400,
            detail="Loan amount and term are required to submit application"
        )
    
    # Run decision logic
    decision = evaluate_loan_decision(
        email=application["email"],
        amount=application["loan_amount"],
        term=application["loan_term"]
    )
    
    return SubmitResponse(
        application=ApplicationResponse(**application),
        decision=decision
    )