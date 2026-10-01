import os
from dotenv import load_dotenv
from database import get_connection

# Load environment variables
load_dotenv()

def check_table():
    """Check if the loan_applications table exists."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Check if table exists
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'loan_applications'
        """)
        
        result = cur.fetchone()
        
        if result:
            print(f"Table found: public.{result[0]}")
            
            # Check columns
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'loan_applications'
                ORDER BY ordinal_position
            """)
            
            columns = cur.fetchall()
            print("\nColumns:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            # Check triggers
            cur.execute("""
                SELECT trigger_name, event_manipulation, action_statement
                FROM information_schema.triggers
                WHERE event_object_table = 'loan_applications'
            """)
            
            triggers = cur.fetchall()
            if triggers:
                print("\nTriggers:")
                for trigger in triggers:
                    print(f"  - {trigger[0]} ({trigger[1]})")
            
            # Check RLS policies
            cur.execute("""
                SELECT policyname, cmd, qual
                FROM pg_policies
                WHERE tablename = 'loan_applications'
            """)
            
            policies = cur.fetchall()
            if policies:
                print("\nRLS Policies:")
                for policy in policies:
                    print(f"  - {policy[0]} ({policy[1]})")
        else:
            print("Table not found: loan_applications")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error checking tables: {e}")

if __name__ == "__main__":
    check_table()