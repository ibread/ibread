#!/bin/bash
perl ./tpch_gen_data.pl ./data.properties
perl ./tpch_create_db.pl ./db.properties
perl ./tpch_load_data.pl ./db.properties
perl ./tpch_create_indexes.pl ./db.properties
perl ./tpch_distributions.pl ./db.properties
