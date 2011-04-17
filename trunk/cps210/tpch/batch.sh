#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage: ${0} NUM"
    exit 1
fi

NUM=${1}

echo "Config..."
sed -i "s/tpch_data = .*$/tpch_data = \/mnt\/pdata${NUM}\//g" db.properties
sed -i "s/tpch_home = .*$/tpch_home = \/mnt\/pdata${NUM}\//g" data.properties

echo "Generating data..."
#perl ./tpch_gen_data.pl ./data.properties
echo "Creating database..."
#perl ./tpch_create_db.pl ./db.properties
echo "Loading data..."
perl ./tpch_load_data.pl ./db.properties
echo "Creating index..."
perl ./tpch_create_indexes.pl ./db.properties
echo "Getting distribution..."
perl ./tpch_distributions.pl ./db.properties
