-- =====================================================
-- Loan Application Database Schema
-- For Supabase PostgreSQL with Auth Integration
-- =====================================================

-- 1. Create loan_applications table
-- This table stores loan application data linked to Supabase Auth users
CREATE TABLE IF NOT EXISTS loan_applications (
    id UUID PRIMARY KEY DEFAULT auth.uid(),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email_address TEXT NOT NULL,
    phone_number TEXT,
    -- Loan details are collected after a user signs up.
    loan_amount DECIMAL(12, 2),
    loan_term INTEGER,
    loan_purpose TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Enable Row Level Security (RLS)
-- This ensures users can only access their own data
ALTER TABLE loan_applications ENABLE ROW LEVEL SECURITY;

-- 3. Create RLS Policies
-- Policy: Users can view their own loan application
CREATE POLICY "Users can view own loan application"
    ON loan_applications
    FOR SELECT
    USING (auth.uid() = id);

-- Policy: Users can insert their own loan application
CREATE POLICY "Users can insert own loan application"
    ON loan_applications
    FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Policy: Users can update their own loan application
CREATE POLICY "Users can update own loan application"
    ON loan_applications
    FOR UPDATE
    USING (auth.uid() = id);

-- Policy: Users can delete their own loan application
CREATE POLICY "Users can delete own loan application"
    ON loan_applications
    FOR DELETE
    USING (auth.uid() = id);

-- 4. Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $func$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

-- 5. Create trigger to update updated_at on row modification
CREATE TRIGGER update_loan_applications_updated_at
    BEFORE UPDATE ON loan_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 6. Create function to handle new user signup
-- This function creates a new row in loan_applications when a user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $func$
BEGIN
    INSERT INTO public.loan_applications (
        id,
        first_name,
        last_name,
        email_address
    )
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'first_name', ''),
        COALESCE(NEW.raw_user_meta_data->>'last_name', ''),
        COALESCE(NEW.email, '')
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$func$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7. Create trigger on auth.users for automatic row creation
-- This trigger fires after a new user is created in Supabase Auth
CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- =====================================================
-- NOTES:
-- - The table uses auth.uid() as the default for the id column
-- - RLS policies ensure data isolation between users
-- - The trigger automatically creates a row when a user signs up
-- - The updated_at column is automatically maintained
-- =====================================================