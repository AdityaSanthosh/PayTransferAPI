import psycopg2

# Insert your db config here
try:
    conn = psycopg2.connect("dbname=transactionsd user=postgres host=localhost password=postgres")
except psycopg2.OperationalError as e:
    raise
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

try:
    cur.execute("CREATE TABLE IF NOT EXISTS transactions"
                "(id uuid PRIMARY KEY DEFAULT gen_random_uuid (),"
                "amount numeric(15,4),"
                "credit_account_no VARCHAR(10) FOREIGN KEY(account_no) REFERENCES balances(account_no) ON DELETE RESTRICT,"
                "debit_account_no VARCHAR(10) FOREIGN KEY(account_no) REFERENCES balances(account_no) ON DELETE RESTRICT,"
                "created_datetime timestamp NOT NULL set default current_timestamp);")
except psycopg2.Error:
    raise

# not null is not really needed when the values are automatically generated but I left it there for intuition

try:
    cur.execute("CREATE TABLE IF NOT EXISTS balances"
                "balance numeric(15,4) NOT NULL,"
                "account_no VARCHAR(10) NOT NULL unique);")
except psycopg2.Error:
    raise

# """
# Creating Indices for faster selects
# """

try:
    cur.execute("create index account_no_lookup on balances (account_no);")
except psycopg2.Error:
    raise

# """
# Some Constraints which are important for consistency
# """

cur.execute("GRANT ALL PRIVILEGES ON DATABASE transactionsdb TO aditya;")
cur.execute("ALTER ROLE aditya SET CLIENT_ENCODING TO 'utf-8';")
cur.execute("ALTER ROLE aditya SET default_transaction_isolation TO 'read committed';")
cur.execute("ALTER ROLE aditya SET TIMEZONE TO 'UTC';")
cur.execute("ALTER TABLE balances ADD CONSTRAINT Check_minimumBalance CHECK (balance >= 100);")
cur.execute("CREATE RULE transactions_delete AS ON DELETE TO transactions DO INSTEAD NOTHING;")

try:
    cur.execute(
        "CREATE or replace PROCEDURE transact(fromacc varchar, toacc varchar, amt numeric, out transactionid uuid) "
        "LANGUAGE plpgsql AS $$ "
        "BEGIN update balances "
        "set balance = balance - amt where account_no = fromacc;"
        " update balances set balance = balance + amt where account_no = toacc; "
        "INSERT INTO transactions(amount, credit_account_no, debit_account_no) VALUES (amt, toacc, fromacc) returning id into transactionid; "
        "END;"
        "$$;")
except psycopg2.Error as e:
    raise

conn.commit()
cur.close()
conn.close()
