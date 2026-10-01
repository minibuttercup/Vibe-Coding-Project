"""
CRUD Operations for Loan Applications

This module provides database operations for loan applications.
All operations verify that the user owns the application before proceeding.
"""

from typing import Optional
from database import get_connection
from decimal import Decimal

# =====================================================
# DATA MODELS (using dictionaries for simplicity)
# =====================================================

def create_loan_application(
    user_id: str,
    first_name: str,
    last_name: str,
    email: str,
    phone: Optional[str] = None,
    loan_amount: Optional[Decimal] = None,
    loan_term: Optional[int] = None,
    loan_purpose: Optional[str] = None
) -> dict:
    """
    Create a new loan application for a user.
    
    Args:
        user_id: Supabase Auth user ID
        first_name: User's first name
        last_name: User's last name
        email: User's email address
        phone: User's phone number (optional)
        loan_amount: Requested loan amount (optional, can be added later)
        loan_term: Loan term in months (optional)
        loan_purpose: Purpose of the loan (optional)
    
    Returns:
        Dictionary with the created application data
    
    Raises:
        Exception: If database operation fails
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Insert the loan application
        cur.execute("""
            INSERT INTO loan_applications (
                id, first_name, last_name, email_address, phone_number,
                loan_amount, loan_term, loan_purpose
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                email_address = EXCLUDED.email_address,
                phone_number = EXCLUDED.phone_number,
                loan_amount = EXCLUDED.loan_amount,
                loan_term = EXCLUDED.loan_term,
                loan_purpose = EXCLUDED.loan_purpose
            RETURNING id, first_name, last_name, email_address, phone_number,
                      loan_amount, loan_term, loan_purpose, created_at, updated_at
        """, (
            user_id, first_name, last_name, email, phone,
            loan_amount, loan_term, loan_purpose
        ))
        
        row = cur.fetchone()
        conn.commit()
        
        return {
            "id": str(row[0]),
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "phone": row[4],
            "loan_amount": float(row[5]) if row[5] else None,
            "loan_term": row[6],
            "loan_purpose": row[7],
            "created_at": row[8].isoformat() if row[8] else None,
            "updated_at": row[9].isoformat() if row[9] else None
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def get_loan_application(user_id: str, application_id: str) -> Optional[dict]:
    """
    Get a loan application by ID.
    
    Verifies that the user owns the application before returning it.
    
    Args:
        user_id: Supabase Auth user ID (for authorization)
        application_id: UUID of the loan application
    
    Returns:
        Dictionary with application data, or None if not found
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, first_name, last_name, email_address, phone_number,
                   loan_amount, loan_term, loan_purpose, created_at, updated_at
            FROM loan_applications
            WHERE id = %s
        """, (application_id,))
        
        row = cur.fetchone()
        
        if not row:
            return None
        
        # Verify ownership (RLS should also enforce this, but double-check)
        if str(row[0]) != user_id:
            return None
        
        return {
            "id": str(row[0]),
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "phone": row[4],
            "loan_amount": float(row[5]) if row[5] else None,
            "loan_term": row[6],
            "loan_purpose": row[7],
            "created_at": row[8].isoformat() if row[8] else None,
            "updated_at": row[9].isoformat() if row[9] else None
        }
    finally:
        cur.close()
        conn.close()


def update_loan_application(
    user_id: str,
    application_id: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    loan_amount: Optional[Decimal] = None,
    loan_term: Optional[int] = None,
    loan_purpose: Optional[str] = None
) -> Optional[dict]:
    """
    Update a loan application.
    
    Only updates fields that are provided (not None).
    Verifies ownership before updating.
    
    Args:
        user_id: Supabase Auth user ID (for authorization)
        application_id: UUID of the loan application
        first_name: New first name (optional)
        last_name: New last name (optional)
        email: New email (optional)
        phone: New phone (optional)
        loan_amount: New loan amount (optional)
        loan_term: New loan term (optional)
        loan_purpose: New loan purpose (optional)
    
    Returns:
        Dictionary with updated application data, or None if not found/not owned
    """
    # First verify ownership
    existing = get_loan_application(user_id, application_id)
    if not existing:
        return None
    
    # Build dynamic update query
    updates = []
    params = []
    
    if first_name is not None:
        updates.append("first_name = %s")
        params.append(first_name)
    if last_name is not None:
        updates.append("last_name = %s")
        params.append(last_name)
    if email is not None:
        updates.append("email_address = %s")
        params.append(email)
    if phone is not None:
        updates.append("phone_number = %s")
        params.append(phone)
    if loan_amount is not None:
        updates.append("loan_amount = %s")
        params.append(loan_amount)
    if loan_term is not None:
        updates.append("loan_term = %s")
        params.append(loan_term)
    if loan_purpose is not None:
        updates.append("loan_purpose = %s")
        params.append(loan_purpose)
    
    if not updates:
        return existing  # Nothing to update
    
    # Add application_id to params
    params.append(application_id)
    
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        query = f"""
            UPDATE loan_applications
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, first_name, last_name, email_address, phone_number,
                      loan_amount, loan_term, loan_purpose, created_at, updated_at
        """
        
        cur.execute(query, params)
        row = cur.fetchone()
        conn.commit()
        
        return {
            "id": str(row[0]),
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "phone": row[4],
            "loan_amount": float(row[5]) if row[5] else None,
            "loan_term": row[6],
            "loan_purpose": row[7],
            "created_at": row[8].isoformat() if row[8] else None,
            "updated_at": row[9].isoformat() if row[9] else None
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def delete_loan_application(user_id: str, application_id: str) -> bool:
    """
    Delete a loan application.
    
    Verifies ownership before deleting.
    
    Args:
        user_id: Supabase Auth user ID (for authorization)
        application_id: UUID of the loan application
    
    Returns:
        True if deleted, False if not found/not owned
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        cur.execute("""
            DELETE FROM loan_applications
            WHERE id = %s
        """, (application_id,))
        
        deleted = cur.rowcount > 0
        conn.commit()
        
        return deleted
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def get_user_application(user_id: str) -> Optional[dict]:
    """
    Get the loan application for a user.
    
    Since the table uses auth.uid() as the primary key,
    each user has exactly one application.
    
    Args:
        user_id: Supabase Auth user ID
    
    Returns:
        Dictionary with application data, or None if not found
    """
    return get_loan_application(user_id, user_id)