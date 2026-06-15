import psycopg2
try:
    conn = psycopg2.connect('host=127.0.0.1 port=5433 dbname=school_admin_db user=postgres password=postgres')
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    tables = cur.fetchall()
    print([t[0] for t in tables])
    
    # Try deleting rows from Django tables directly
    if 'students_parentinfo' in [t[0] for t in tables]:
        cur.execute("TRUNCATE TABLE students_studentprofile CASCADE;")
        conn.commit()
        print("Truncated tables.")
    else:
        print("No students_parentinfo table found.")
    conn.close()
except Exception as e:
    print(e)
