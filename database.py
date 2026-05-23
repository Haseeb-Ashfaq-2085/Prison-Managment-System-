import pyodbc
import pandas as pd
import streamlit as st

# ==========================================
# ⚙️ DATABASE CONFIGURATION
# ==========================================
SERVER_NAME = r'.\SQLEXPRESS'
DATABASE_NAME = 'PrisonManagement'

# ==========================================
# 🔌 DATABASE CONNECTION
# ==========================================
def get_connection():
    try:
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={SERVER_NAME};"
            f"DATABASE={DATABASE_NAME};"
            "Trusted_Connection=yes;"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        st.error(f"❌ Database Connection Failed: {e}")
        return None


# ▶️ EXECUTE PROCEDURE (INSERT / UPDATE / DELETE)


def execute_procedure(proc_name, params=None):
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        if params is not None:
            if not isinstance(params, (tuple, list)):
                params = (params,)

            placeholders = ",".join(["?"] * len(params))
            cursor.execute(f"EXEC {proc_name} {placeholders}", params)
        else:
            cursor.execute(f"EXEC {proc_name}")

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        st.error(f"❌ Procedure Execution Failed: {e}")
        return False

    finally:
        conn.close()




# 📥 FETCH PROCEDURE (SELECT)

def fetch_procedure(proc_name, params=None):
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()

    try:
        if params is not None:
            if not isinstance(params, (tuple, list)):
                params = (params,)

            placeholders = ",".join(["?"] * len(params))
            query = f"EXEC {proc_name} {placeholders}"
            df = pd.read_sql(query, conn, params=params)
        else:
            df = pd.read_sql(f"EXEC {proc_name}", conn)

        return df

    except Exception as e:
        st.error("❌ Fetch Procedure Failed")
        st.code(str(e))
        return pd.DataFrame()

    finally:
        conn.close()


# 📄 FETCH ONE ROW
def fetch_one(query, params=None):
    conn = get_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        return cursor.fetchone()

    except Exception as e:
        st.error(f"❌ Fetch One Error: {e}")
        return None

    finally:
        conn.close()
