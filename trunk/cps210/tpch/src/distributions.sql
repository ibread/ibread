-- customer
select count(distinct c_nationkey) as c_nationkey_count from customer;
select c_nationkey, count(1) as cnt from customer group by c_nationkey order by cnt desc limit 20;
select c_nationkey, count(1) as cnt from customer group by c_nationkey order by cnt asc limit 20;

select count(distinct c_acctbal) as c_acctbal_count from customer;
select c_acctbal, count(1) as cnt from customer group by c_acctbal order by cnt desc limit 20;
select c_acctbal, count(1) as cnt from customer group by c_acctbal order by cnt asc limit 20;


-- orders
select count(distinct o_custkey) as o_custkey_count from orders;
select o_custkey, count(1) as cnt from orders group by o_custkey order by cnt desc limit 20;
select o_custkey, count(1) as cnt from orders group by o_custkey order by cnt asc limit 20;

select count(distinct o_totalprice) as o_totalprice_count from orders;
select o_totalprice, count(1) as cnt from orders group by o_totalprice order by cnt desc limit 20;
select o_totalprice, count(1) as cnt from orders group by o_totalprice order by cnt asc limit 20;

select count(distinct o_orderdate) as o_orderdate_count from orders;
select o_orderdate, count(1) as cnt from orders group by o_orderdate order by cnt desc limit 20;
select o_orderdate, count(1) as cnt from orders group by o_orderdate order by cnt asc limit 20;


-- part
select count(distinct p_brand) as p_brand_count from part;
select p_brand, count(1) as cnt from part group by p_brand order by cnt desc limit 20;
select p_brand, count(1) as cnt from part group by p_brand order by cnt asc limit 20;

select count(distinct p_size) as p_size_count from part;
select p_size, count(1) as cnt from part group by p_size order by cnt desc limit 20;
select p_size, count(1) as cnt from part group by p_size order by cnt asc limit 20;


-- supplier
select count(distinct s_nationkey) as s_nationkey_count from supplier;
select s_nationkey, count(1) as cnt from supplier group by s_nationkey order by cnt desc limit 20;
select s_nationkey, count(1) as cnt from supplier group by s_nationkey order by cnt asc limit 20;

select count(distinct s_acctbal) as s_acctbal_count from supplier;
select s_acctbal, count(1) as cnt from supplier group by s_acctbal order by cnt desc limit 20;
select s_acctbal, count(1) as cnt from supplier group by s_acctbal order by cnt asc limit 20;


-- partsupp
select count(distinct ps_availqty) as ps_availqty_count from partsupp;
select ps_availqty, count(1) as cnt from partsupp group by ps_availqty order by cnt desc limit 20;
select ps_availqty, count(1) as cnt from partsupp group by ps_availqty order by cnt asc limit 20;

select count(distinct ps_supplycost) as ps_supplycost_count from partsupp;
select ps_supplycost, count(1) as cnt from partsupp group by ps_supplycost order by cnt desc limit 20;
select ps_supplycost, count(1) as cnt from partsupp group by ps_supplycost order by cnt asc limit 20;

-- lineitem
select count(distinct l_orderkey) as l_orderkey_count from lineitem;
select l_orderkey, count(1) as cnt from lineitem group by l_orderkey order by cnt desc limit 20;
select l_orderkey, count(1) as cnt from lineitem group by l_orderkey order by cnt asc limit 20;

select count(distinct l_partkey) as l_partkey_count from lineitem;
select l_partkey, count(1) as cnt from lineitem group by l_partkey order by cnt desc limit 20;
select l_partkey, count(1) as cnt from lineitem group by l_partkey order by cnt asc limit 20;

select count(distinct l_suppkey) as l_suppkey_count from lineitem;
select l_suppkey, count(1) as cnt from lineitem group by l_suppkey order by cnt desc limit 20;
select l_suppkey, count(1) as cnt from lineitem group by l_suppkey order by cnt asc limit 20;

select count(distinct l_quantity) as l_quantity_count from lineitem;
select l_quantity, count(1) as cnt from lineitem group by l_quantity order by cnt desc limit 20;
select l_quantity, count(1) as cnt from lineitem group by l_quantity order by cnt asc limit 20;

select count(distinct l_shipdate) as l_shipdate_count from lineitem;
select l_shipdate, count(1) as cnt from lineitem group by l_shipdate order by cnt desc limit 20;
select l_shipdate, count(1) as cnt from lineitem group by l_shipdate order by cnt asc limit 20;

select count(distinct l_commitdate) as l_commitdate_count from lineitem;
select l_commitdate, count(1) as cnt from lineitem group by l_commitdate order by cnt desc limit 20;
select l_commitdate, count(1) as cnt from lineitem group by l_commitdate order by cnt asc limit 20;

select count(distinct l_receiptdate) as l_receiptdate_count from lineitem;
select l_receiptdate, count(1) as cnt from lineitem group by l_receiptdate order by cnt desc limit 20;
select l_receiptdate, count(1) as cnt from lineitem group by l_receiptdate order by cnt asc limit 20;

