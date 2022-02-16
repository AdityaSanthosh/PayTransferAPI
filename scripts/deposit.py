import psycopg2

conn = psycopg2.connect("dbname=transactionsdb user=postgres host=localhost password=postgres")
cur = conn.cursor()

cur.execute("INSERT INTO balances(balance,account_no) VALUES (1000,'1234567');")
cur.execute("INSERT INTO balances(balance,account_no) VALUES (100,'7654321');")

conn.commit()
cur.close()
conn.close()
