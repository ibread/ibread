------------------------------------------------------------------
alter table nation   drop constraint fk_r_regionkey;
alter table customer drop constraint fk_n_nationkey;
alter table orders   drop constraint fk_c_custkey;
alter table supplier drop constraint fk_n_nationkey;
alter table partsupp drop constraint fk_p_partkey;
alter table partsupp drop constraint fk_s_suppkey;
alter table lineitem drop constraint fk_o_orderkey;
alter table lineitem drop constraint fk_s_suppkey;
alter table lineitem drop constraint fk_ps_partkey_suppkey;
alter table lineitem drop constraint fk_p_partkey;

------------------------------------------------------------------
alter table region   drop constraint region_pkey;
alter table nation   drop constraint nation_pkey;
alter table customer drop constraint customer_pkey;
alter table orders   drop constraint orders_pkey;
alter table part     drop constraint part_pkey;
alter table supplier drop constraint supplier_pkey;
alter table partsupp drop constraint partsupp_pkey;
alter table lineitem drop constraint lineitem_pkey;

