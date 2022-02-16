"""
I do not know SQL beyond selects, joins, aggregates. These variations of SQL functions, procedures are part of my rapid iterative learning.
*Not assosciated with the actual code


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

select * from balances;

create or replace function transact(in fromacc varchar,in toacc varchar,in amt numeric) RETURNS uuid as $$
        declare @from_bal numeric;
        select balance from balances where account_no = fromacc into @from_bal;
        update balances
        set balance = balance - amt
        where account_no = fromacc and balance = @from_bal;
        update balances
        set balance = balance + amt
        where account_no = toacc;
        INSERT INTO transactions(amount, credit_account_no, debit_account_no) VALUES (amt, toacc, fromacc) RETURNING id;
--         EXCEPTION WHEN UNIQUE_VIOLATION THEN     -- inserted in concurrent session.
--             RAISE NOTICE 'Transaction ID already exists!';
    $$ LANGUAGE sql;

select transact('1234567','7654321',100);

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

CREATE or replace PROCEDURE transaction(fromacc varchar, toacc varchar, amt numeric, out transactionid uuid)
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
    commit;
END;
$$;

    create procedure transact(fromacc varchar, toacc varchar, amt numeric, OUT tid uuid) AS $$
            update balances
            set balance = balance - amt
            where account_no = fromacc;
            update balances
            set balance = balance + amt
            where account_no = toacc;
            commit;
            INSERT INTO transactions(amount, credit_account_no, debit_account_no) VALUES (amt, toacc, fromacc) RETURNING id;
        $$ LANGUAGE SQL;


create procedure transact(fromacc varchar, toacc varchar, amt numeric) AS $$
            update balances
            set balance = balance - amt
            where account_no = fromacc;
            update balances
            set balance = balance + amt
            where account_no = toacc;
            commit;
            INSERT INTO transactions(amount, credit_account_no, debit_account_no) VALUES (amt, toacc, fromacc);
        $$ LANGUAGE SQL;


CREATE or replace PROCEDURE transaction(fromacc varchar, toacc varchar, amt numeric, out transactionid uuid)
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
    commit;
END;
$$;
"""
