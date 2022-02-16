import psycopg2

conn = psycopg2.connect("dbname=transactionsdb user=postgres host=localhost password=postgres")
cur = conn.cursor()

cur.execute("INSERT INTO balances(id,balance,account_no) VALUES (1,1000,1234567);")

conn.commit()
cur.close()
conn.close()
