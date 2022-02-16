import psycopg2
# Insert your db config here
conn = psycopg2.connect("dbname=transactionsdb user=postgres host=localhost password=postgres")
cur = conn.cursor()

# python Model
"""
TABLE transactions
  - id (unique)
  - amount
  - account_no
  - created_datetime

TABLE balances
  - account_no (unique)
  - balance

TABLE account_type
  - type (joint, business, personal)
"""

"""
Creating Tables
"""
cur.execute("CREATE TABLE IF NOT EXISTS transactions"
            "(id uuid PRIMARY KEY DEFAULT gen_random_uuid (),"
            "amount numeric(15,4),"
            "credit_account_no VARCHAR(10) FOREIGN KEY(account_no) REFERENCES balances(account_no) ON DELETE RESTRICT,"
            "debit_account_no VARCHAR(10) FOREIGN KEY(account_no) REFERENCES balances(account_no) ON DELETE RESTRICT,"
            "created_datetime timestamp NOT NULL set default current_timestamp);")
# not null is not really needed when the values are automatically generated but I left it there for intuition

cur.execute("CREATE TABLE IF NOT EXISTS balances"
            "balance numeric(15,4) NOT NULL,"
            "account_no VARCHAR(10) NOT NULL unique);")

"""
Creating Indices for faster selects
"""
cur.execute("CREATE INDEX account_no_lookup ON balances(account_no);")

cur.execute("create index account_no_lookup on balances (account_no);")

"""
Some Constraints which are important for consistency
"""
cur.execute("GRANT ALL PRIVILEGES ON DATABASE transactionsdb TO aditya;")
cur.execute("ALTER ROLE aditya SET CLIENT_ENCODING TO 'utf-8';")
cur.execute("ALTER ROLE aditya SET default_transaction_isolation TO 'read committed';")
cur.execute("ALTER ROLE aditya SET TIMEZONE TO 'UTC';")
cur.execute("ALTER TABLE balances ADD CONSTRAINT Check_minimumBalance CHECK (balance >= 100);")
cur.execute("CREATE RULE transactions_delete AS ON DELETE TO transactions DO INSTEAD NOTHING;")



conn.commit()
cur.close()
conn.close()




