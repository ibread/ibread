#!/usr/bin/perl -w

###############################################################################
# Create a TPC-H database, load the schema and the constraints.
#
# Usage: perl tpch_create_db.pl db.properties
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
$DB_NAME  = $opt{'dbname'};
$USERNAME = $opt{'username'};
$PG_BIN   = $opt{'pgdir'};

# Output input parameters
!system qq(date) or die $!;
println "Input Parameters:";
println "DBName: $DB_NAME";
println "Username: $USERNAME";
println "PSQL bin dir: $PG_BIN";
println "";

# Ask for confirmation
println "This script will drop database $DB_NAME if it exists";
print "Are you sure (yes/no): ";

#Commented by Zhiqiu, for batch task
#$| = 1;
#$_ = <STDIN>;
#chomp;
#
#if ( $_ ne "yes" )
#{
#   exit(0);
#}

# Create the database and load the schema
println "Creating database $DB_NAME";
!system qq($PG_BIN/psql -d postgres).
        qq( -c 'drop database if exists $DB_NAME' > /dev/null) or die $!;
!system qq($PG_BIN/psql -d postgres).
        qq( -c 'create database $DB_NAME' > /dev/null) or die $!;
println "Database created";

println "Loading database schema";
!system qq($PG_BIN/psql -U $USERNAME -d $DB_NAME).
        qq( -f src/schema.sql > /dev/null) or die $!;
!system qq($PG_BIN/psql -U $USERNAME -d $DB_NAME).
        qq( -f src/add_constraints.sql > /dev/null) or die $!;
println "Schema is loaded";

# Done
$current = `date`; $current =~ s/\s+$//;
println qq{Done at $current};

$time = time - $^T;
println "Time taken (sec): \t$time";

