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
    try:
        data = json.loads(request.data)
    except json.JSONDecodeError:
        return json.dumps({'message': 'Please Enter the Input in the JSON format correctly'})
    try:
        assert len(data) == 2
    except AssertionError:
        return json.dumps({'message': 'Remove any additional fields other than account and amount'})
    try:
        account = data['account']
        amount = int(data["amount"])
    except KeyError:
        return json.dumps({'message': 'Please Enter the Input in 2 fields. account and amount. both strings'})
    try:
        cur.execute("UPDATE balances SET balance = balance + %s WHERE account_no = %s;", (amount, account))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        print(e.pgerror)
    cur.execute("SELECT balance FROM balances WHERE account_no=%s;", (account,))
    balance = cur.fetchone()
    return json.dumps({'account': account, 'balance': balance, 'message': 'success'}, cls=DecimalEncoder)


@app.route('/transfer', methods=['POST'])
def transfer():
    # if user.ongoingtransaction:
    #   return "You sent request multiple times" or drop the transaction
    # user.ongoingtransaction = True
    assert request.path == '/transfer'
    assert request.method == 'POST'
    try:
        data = json.loads(request.data)
    except json.JSONDecodeError:
        return json.dumps({'message': 'Please Enter the Input in the JSON format correctly'})
    from_account = data['from']
    to_account = data["to"]
    try:
        amount = int(data["amount"])
    except ValueError:
        return json.dumps({'message': 'Please Enter a Number for input'})
    try:
        assert len(data) == 3
    except AssertionError:
        return json.dumps({'message': 'Remove any additional fields other than from_account, to_account and amount'})
    try:
        assert amount > 0
    except AssertionError:
        return json.dumps({'message': 'Please Enter Positive Values of Amount'})
    errormsg = "Oops! Something wrong on our servers. Don't worry. Your transaction is already rolled back."
    try:
        cur.execute("call transact(%s,%s,%s,null);", (from_account, to_account, amount))
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if e.pgcode == '23514':
            return json.dumps({'message': "Balance Insufficient"})
        if e.pgcode == '23503':
            return json.dumps({'message': "No Such Accounts present in the System. Please Check if you entered the "
                                          "proper Account Number"})
        else:
            print(e.pgcode, e.pgerror)
            return json.dumps({"message": errormsg})
    except psycopg2.OperationalError as e:
        conn.rollback()
        print(e.pgcode, e.pgerror)
        return json.dumps({"message": errormsg})
    except psycopg2.InternalError as e:
        conn.rollback()
        print(e.pgcode, e.pgerror)
        return json.dumps({"message": errormsg})
    except psycopg2.ProgrammingError as e:
        conn.rollback()
        print(e.pgcode, e.pgerror)
        return json.dumps({"message": errormsg})
    except psycopg2.DatabaseError as e:
        conn.rollback()
        print(e.pgcode, e.pgerror)
        return json.dumps({"message": errormsg})
    except psycopg2.Error as e:
        conn.rollback()
        print(e.pgerror, e.pgcode)
        return json.dumps({"message": errormsg})
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
    transaction_id_clean = [data for data in transaction_id][0]
    cur.execute(f"select created_datetime from transactions where id = '{transaction_id_clean}';")
    created_at = cur.fetchone()
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
        "created_datetime": created_at,
        "message": "Success"
    }
    # user.ongoingtransaction = False
    return json.dumps(response, cls=DecimalEncoder, default=str)


if __name__ == '__main__':
    app.run()
