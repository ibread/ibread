-- Indexes on nation
create index nation_1_idx on nation(n_regionkey, n_nationkey);
create index nation_2_idx on nation(n_name, n_nationkey);

-- Indexes on supplier
create index supplier_1_idx on supplier(s_nationkey, s_suppkey);

-- Indexes on partsupp
create index partsupp_1_idx on partsupp(ps_suppkey, ps_partkey);

-- Indexes on customer
create index customer_1_idx on customer(c_acctbal, c_custkey);
create index customer_2_idx on customer(c_nationkey, c_custkey);

-- Indexes on orders
create index orders_1_idx on orders(o_orderdate);
create index orders_2_idx on orders(o_custkey);

-- Indexes on part
create index part_1_idx on part(p_type, p_partkey);

-- Indexes on lineitem
create index lineitem_1_idx on lineitem(l_partkey,l_discount);
create index lineitem_2_idx on lineitem(l_shipdate,l_discount);
create index lineitem_3_idx on lineitem(l_returnflag,l_discount);
create index lineitem_4_idx on lineitem(l_partkey,l_quantity);

