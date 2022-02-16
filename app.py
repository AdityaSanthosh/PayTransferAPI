import decimal

from flask import Flask
from flask import request
import psycopg2
import json


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


app = Flask(__name__)

conn = psycopg2.connect("dbname=transactionsdb user=postgres host=localhost password=postgres")
cur = conn.cursor()


# use login_required here
@app.route('/deposit', methods=['POST'])
def deposit():
    assert request.path == '/deposit'
    assert request.method == 'POST'
    data = json.loads(request.data)
    account = data['from']
    amount = Decimal(data["amount"])
    balance = None
    # not finished. example script already present in deposit.py
    return json.dumps({'account': account, 'balance': balance, 'message': 'success/failed'})


@app.route('/transfer', methods=['POST'])
def transfer():
    assert request.path == '/transfer'
    assert request.method == 'POST'
    data = json.loads(request.data)
    from_account = data['from']
    to_account = data["to"]
    amount = int(data["amount"])
    cur.execute("call transact(%s,%s,%s,null);", (from_account, to_account, amount))
    """ This one works too...
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
    """
    conn.commit()
    transaction_id = cur.fetchone()
    cur.execute(f"select balance from balances where account_no = '{from_account}';")
    from_balance = cur.fetchone()
    cur.execute(f"select balance from balances where account_no = '{to_account}';")
    to_balance = cur.fetchone()
    response = {
        "id": transaction_id,
        "from": {
            "id": from_account,
            "balance": from_balance
        },
        "to": {
            "id": to_account,
            "balance": to_balance
        },
        "transfered": amount,
    }
    return json.dumps(response, cls=DecimalEncoder)


if __name__ == '__main__':
    app.run()
