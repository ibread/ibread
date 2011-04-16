#!/usr/bin/perl -w

###############################################################################
# Creates indexes for a TPC-H database. The database must exist.
#
# Usage: perl tpch_create_indexes.pl db.properties
#
# Parameters Used: dbname, username, pgdir
#
# Author: Herodotos Herodotou
# Date: May 31, 2010
#
##############################################################################

use lib "./src";
use GetOptions qw(get_options println);

# Error checking
if ($#ARGV != 0)
{
   print qq(Usage: perl $0 db.properties\n);
   exit(-1);
}

# Get input parameters
%opt = get_options($ARGV[0]);
$DB_NAME   = $opt{'dbname'};
$USERNAME  = $opt{'username'};
$PG_BIN    = $opt{'pgdir'};

# Output input parameters
!system qq(date) or die $!;
println "Input Parameters:";
println "DBName: $DB_NAME";
println "Username: $USERNAME";
println "PSQL bin dir: $PG_BIN";
println "";

# Create indexes
println qq(Creating the indexes);
!system qq($PG_BIN/psql -U $USERNAME -d $DB_NAME -a -f src/indexes.sql) or die $!;
println qq(Index creation is complete);

# Analyze--update statistics for the all tables in the database
println qq(Analyzing the tables);
!system qq($PG_BIN/psql -U $USERNAME -d $DB_NAME -c "ANALYZE" > /dev/null) or die $!;
println qq{Done!};

$time = time-$^T;
println "Time taken (sec): \t$time";

