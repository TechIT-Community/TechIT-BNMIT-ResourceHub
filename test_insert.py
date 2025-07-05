import psycopg2

hostname = 'localhost'
database = 'demodb'
username = 'postgres'
pwd = 'admin'
port_id = 5432
cur = None
conn = None

try:
    conn = psycopg2.connect(
        host=hostname,
        dbname=database,
        user=username,
        password=pwd,
        port=port_id
    )

    cur = conn.cursor()

    insert_script = '''
    INSERT INTO resources 
    (id, title, subject, semester, department, type, source, link, last_updated) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    insert_value = (1, 'Regression', 'AIML', '3', 'CSE', 'PDF', 'Github', 'jajaja', '2020-06-22 19:10:25')
    cur.execute(insert_script, insert_value)

    conn.commit()  # 🔴 CRUCIAL STEP

    print("✅ Record inserted successfully.")

except Exception as e:
    print("❌ Error:", e)

finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
