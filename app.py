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
    return json.dumps({'account': account, 'balance': balance, 'message': 'success/failed'})


@app.route('/transfer', methods=['POST'])
def transfer():
    assert request.path == '/transfer'
    assert request.method == 'POST'
    data = json.loads(request.data)
    from_account = data['from']
    to_account = data["to"]
    amount = int(data["amount"])
    try:
        cur.execute("select transact(%s,%s,%s);", (from_account, to_account, amount))
    except:
        return Exception
    transaction_id = cur.fetchone()
    cur.execute(f"select balance from balances where account_no = '{from_account}';")
    from_account_bal = cur.fetchone()
    response = {
        "id": transaction_id,
        "from": {
            "id": from_account,
            "balance": from_account_bal
        },
        "to": {
            "id": to_account,
            "balance": "current_balance"
        },
        "transfered": amount,
        "created_datetime": "transaction created time"
    }
    return json.dumps(response, cls=DecimalEncoder)


if __name__ == '__main__':
    app.run()
