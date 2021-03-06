### Setup Instructions

###### Build from Source
1. Download Postgres, an API testing tool (I used Insomnia). Install them
2. `git clone` this repo. Create a virtual environment.  Install the packages in `requirements.txt` file
3. Spin up a new server and a new postgres database. Replace the database configuration present in the `app.py` file with that of your database
4. Run the instructions present in the `setup.py` in psql. It has the configuration to create database tables, add checks and constraints. Deposit some money at `/deposit` path to facilitate transfers.
5.  Run `flask run` after exporting the env variables. Check the official flask docs if necessary.
6. Send a post request to `localhost:5000` (flask port) in json format with the input format mentioned below.
7. You can see the output in the insomnia/ postman terminal.

###### Docker Image
A `Dockerfile` and `docker-compose` is present in the root directory.
1. Download and install Docker
2. Run `docker-compose up -d --build` which pulls the official python image, installs all the necessary packages, spins up 2 containers running
`flask` and `postgres`.
3. Using `Insomnia` or `postman` (api testing tool), send requests in below input format at `http://192.168.99.100:5000/deposit` and `http://192.168.99.100:5000/transfer`.
4. Happy Testing!!

### Input format:

##### _Deposit_

`{ "from": "account_no",
    "to": "account_no",
    "amount": "money"}`

##### _Transfer_
`{ "from": "account_no",
    "to": "account_no",
    "amount": "money"}`

##### Requirements for a Payment Transaction Database

1. ACID compliance (RDBMS)
2. Indices on accounts to make lookups faster
3. Preventing Race conditions and deadlocks
4. Parameterized SQL queries to prevent SQL Injection
5. No float operations since they are incorrect. Numeric or decimal data types should be used.
6. Consistency and Availability


##### DB Design for this project:

TABLE transactions
  - id (unique)
  - amount
  - account_no (foreignkey)
  - created_datetime

TABLE balances
  - account_no (unique)
  - balance

The `variations.py` contains some interesting trivia. (*Not a part of the project)

_**I tried to implement most of the logic in SQL as stored procedures. This is due to the fact/opinion that database engines are extremely fast than python and the presence of `begin commit rollback` is very valuable**_

Other Technical details are present in `considerations.txt` file in the repository

##### _The Important part of the code for the impatient_

```
CREATE or replace PROCEDURE transact(fromacc varchar, toacc varchar, amt numeric, out transactionid uuid)
LANGUAGE plpgsql
AS $$
BEGIN
    update balances
            set balance = balance - amt
            where account_no = fromacc;
            update balances
            set balance = balance + amt
            where account_no = toacc;
            INSERT INTO transactions(amount, credit_account_no, debit_account_no) VALUES (amt, toacc, fromacc)
            returning id into transactionid;
END;
$$;
```

NOTE: Ideally, you want to check the database if the changes are being committed or not. It is in this project.