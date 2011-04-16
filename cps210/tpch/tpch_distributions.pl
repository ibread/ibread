#!/usr/bin/perl -w

###############################################################################
# Collects column distributions from a TPC-H database. The database must exist.
# The output file will contain
#    (a) the number of unique values
#    (b) the 20 most frequent values
#    (c) the 20 least frequent values
# for important columns from each table.
#
# Usage: perl tpch_distributions.pl db.properties
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

# Execute queries to calculate data distributions
$outputFile = "distributions_$DB_NAME.txt";
println qq(Getting data distributions - This might take a while);
!system qq($PG_BIN/psql -U $USERNAME -d $DB_NAME).
        qq( -f src/distributions.sql > $outputFile) or die $!;
println qq(Done! Generated file $outputFile);

$time = time-$^T;
println "Time taken (sec): \t$time";

