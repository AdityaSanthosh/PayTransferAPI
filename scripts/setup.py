import psycopg2
conn = psycopg2.connect("dbname=transactionsdb user=postgres host=localhost password=postgres")
cur = conn.cursor()

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

cur.execute("CREATE INDEX account_no_lookup ON balances(account_no);")

cur.execute("create or replace function transact(fromacc varchar,toacc varchar, amt numeric) RETURNS uuid as $$ "
            "update balances set balance = balance - amt where account_no = fromacc;"
            "select balance from balances where account_no = fromacc;"
            "update balances set balance = balance + amt where account_no = toacc;"
            "INSERT INTO transactions(amount, credit_account_no, debit_account_no) "
            "VALUES (amt, toacc, fromacc) RETURNING id;"
            "--         EXCEPTION WHEN UNIQUE_VIOLATION THEN     -- "
            "inserted in concurrent session.--             RAISE NOTICE 'Transaction ID already exists!';  "
            "$$ "
            "LANGUAGE sql;")
conn.commit()
cur.close()
conn.close()

# python Model
"""y
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
ALTER TABLE transactions
ADD FOREIGN KEY(account_no) REFERENCES balances(account_no) ON DELETE RESTRICT
GRANT ALL PRIVILEGES ON DATABASE transactionsdb TO aditya
ALTER ROLE aditya SET CLIENT_ENCODING TO 'utf-8'
ALTER ROLE aditya SET default_transaction_isolation TO 'read committed'
ALTER ROLE aditya SET TIMEZONE TO 'UTC';
ALTER TABLE balances
ADD CONSTRAINT Check_minimumBalance
CHECK (balance >= 100)
CREATE RULE transactions_delete AS ON DELETE TO transactions DO INSTEAD NOTHING;


begin;
update balances
        set balance = balance - 100::numeric(15,4)
        where account_no = '1234567';
select balance from balances where account_no = '1234567';
        update balances
        set balance = balance + 100::numeric(15,4)
        where account_no = '7654321';
        INSERT INTO transactions(amount, credit_account_no, debit_account_no) VALUES (100, '1234567', '7654321');
commit;
"""
