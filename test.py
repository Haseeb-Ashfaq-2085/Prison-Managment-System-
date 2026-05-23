import pyodbc

# CONFIGURATION
SERVER = r'.\SQLEXPRESS'   # check if this is correct
DATABASE = 'prison'

print("--- TESTING DATABASE CONNECTION ---")
print(f"Target: {SERVER} -> {DATABASE}")

connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

try:
    # 1. Try Connecting
    conn = pyodbc.connect(connection_string, timeout=5)
    print("✅ CONNECTION SUCCESSFUL!")
    
    # 2. Try Reading Users
    cursor = conn.cursor()
    cursor.execute("SELECT Email, Password, Role FROM Users")
    rows = cursor.fetchall()
    
    if not rows:
        print("⚠️ Connection worked, but NO USERS found in the table.")
    else:
        print(f"✅ Found {len(rows)} users in database:")
        for row in rows:
            print(f"   - Email: {row[0]} | Password: {row[1]} | Role: {row[2]}")
            
    conn.close()

except Exception as e:
    print("\n❌ CONNECTION FAILED!")
    print("Error Details:", e)
    print("\nSUGGESTIONS:")
    print("1. Check if '.\SQLEXPRESS' is the correct Server Name in SSMS.")
    print("2. Ensure SQL Server service is running.")