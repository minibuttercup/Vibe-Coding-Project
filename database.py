import os
import re
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_connection():
    """Get a connection to the Supabase PostgreSQL database."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    
    conn = psycopg2.connect(database_url)
    return conn

def _split_sql_statements(sql_script):
    """Split SQL script into individual statements, respecting dollar-quoted strings."""
    statements = []
    current = []
    in_dollar_quote = False
    dollar_tag = None
    i = 0
    text = sql_script

    while i < len(text):
        # Check for dollar-quote start/end
        if not in_dollar_quote:
            match = re.match(r'\$([a-zA-Z_]*)\$', text[i:])
            if match:
                tag = match.group(1)
                dollar_tag = '$' + tag + '$'
                in_dollar_quote = True
                current.append(dollar_tag)
                i += len(dollar_tag)
                continue
        else:
            if text[i:].startswith(dollar_tag):
                current.append(dollar_tag)
                i += len(dollar_tag)
                in_dollar_quote = False
                dollar_tag = None
                continue

        # If we hit a semicolon outside a dollar-quoted string, it's a statement boundary
        if text[i] == ';' and not in_dollar_quote:
            current.append(';')
            stmt = ''.join(current).strip()
            # Strip leading comment-only lines but keep the statement
            lines = stmt.split('\n')
            # Remove purely empty lines at the start
            while lines and not lines[0].strip():
                lines.pop(0)
            cleaned = '\n'.join(lines).strip()
            if cleaned:
                statements.append(cleaned)
            current = []
            i += 1
            continue

        current.append(text[i])
        i += 1

    # Handle any trailing content without a semicolon
    remaining = ''.join(current).strip()
    if remaining:
        statements.append(remaining)

    return statements


def init_database():
    """Initialize the database by running SQL scripts."""
    # Read the SQL file
    sql_file_path = os.path.join("sql", "init.sql")
    with open(sql_file_path, "r") as f:
        sql_script = f.read()
    
    # Connect and execute
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Split the script into statements, respecting dollar-quoted strings
        statements = _split_sql_statements(sql_script)
        
        # Execute each statement
        for statement in statements:
            if statement.strip():
                try:
                    cur.execute(statement)
                    conn.commit()
                except psycopg2.errors.DuplicateTable:
                    # Table already exists, skip
                    conn.rollback()
                except psycopg2.errors.DuplicateObject:
                    # Object already exists (policy, trigger, etc.), skip
                    conn.rollback()
                except Exception as e:
                    conn.rollback()
                    print(f"Warning: {e}")
        
        cur.close()
        print("Database initialization completed successfully")
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()