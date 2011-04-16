------------------------------------------------------------------
alter table region   add primary key (r_regionkey);
alter table nation   add primary key (n_nationkey);
alter table customer add primary key (c_custkey);
alter table orders   add primary key (o_orderkey);
alter table part     add primary key (p_partkey);
alter table supplier add primary key (s_suppkey);
alter table partsupp add primary key (ps_partkey, ps_suppkey);
alter table lineitem add primary key (l_orderkey, l_linenumber);

------------------------------------------------------------------
alter table nation   add constraint fk_r_regionkey
	foreign key (n_regionkey) references region(r_regionkey);
alter table customer add constraint fk_n_nationkey
	foreign key (c_nationkey) references nation(n_nationkey);
alter table orders   add constraint fk_c_custkey
	foreign key (o_custkey) references customer(c_custkey);
alter table supplier add constraint fk_n_nationkey
	foreign key (s_nationkey) references nation(n_nationkey);
alter table partsupp add constraint fk_p_partkey
	foreign key (ps_partkey)  references part(p_partkey);
alter table partsupp add constraint fk_s_suppkey
	foreign key (ps_suppkey)  references supplier(s_suppkey);
alter table lineitem add constraint fk_o_orderkey
	foreign key (l_orderkey)  references orders(o_orderkey);
alter table lineitem add constraint fk_s_suppkey
	foreign key (l_suppkey)   references supplier(s_suppkey);
alter table lineitem add constraint fk_ps_partkey_suppkey
	foreign key (l_partkey, l_suppkey) 
	                          references partsupp(ps_partkey, ps_suppkey);
alter table lineitem add constraint fk_p_partkey
	foreign key (l_partkey)   references part(p_partkey);

