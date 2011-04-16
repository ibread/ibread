#!/usr/bin/perl -w

###############################################################################
# Load TPC-H data into a database. The data must already be generated and
# the database must exist.
#
# Usage: perl tpch_load_data.pl db.properties
#
# Parameters Used: dbname, username, pch_data, pgdir
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
$TPCH_DATA = $opt{'tpch_data'};
$PG_BIN    = $opt{'pgdir'};

# Output input parameters
!system qq(date) or die $!;
println "Input Parameters:";
println "DBName: $DB_NAME";
println "Username: $USERNAME";
println "TPCH data dir: $TPCH_DATA";
println "PSQL bin dir: $PG_BIN";
println "";

# Check if the directory exists
if (! -e $TPCH_DATA)
{
   println "The directory $TPCH_DATA does not exist";
   exit(-1);
}

# Drop all constraints
println "Dropping all database constraints";
!system qq($PG_BIN/psql -U $USERNAME -d $DB_NAME).
        qq( -f src/drop_constraints.sql > /dev/null) or die $!;
println "Constraints are dropped";

# Import data
println "Importing the data...";
@tables = ("region", "nation", "customer", "orders", 
           "part", "supplier", "partsupp", "lineitem");
foreach $table (@tables)
{
	println "";
	$current = `date`; $current =~ s/\s+$//;

	# Get all the files for this table
	opendir(DH, $TPCH_DATA) or die qq(Can't open $TPCH_DATA: $!);
	my @files = grep { /^$table\.tbl/ } readdir(DH);
	@files = sort(@files);
	close DH;

	# Importing the data to table
	$current = `date`; $current =~ s/\s+$//;
	println qq(Importing  data for $table at $current);

	my $file_count = 0;
	foreach $file (@files)
	{
		my $query = qq(COPY $table FROM '$TPCH_DATA/$file' WITH DELIMITER AS '|' NULL AS '');
		!system qq($PG_BIN/psql -U $USERNAME -d $DB_NAME -c "$query" > /dev/null) or die $!;
		$file_count = $file_count+1;
		print qq(Percentage complete is: ), $file_count*100/($#files+1), qq(%\n);
	}
	println qq($table data is imported);
}
println qq(Data is imported);
println "";


# Add the constraints
$current = `date`; $current =~ s/\s+$//;
println qq(Adding all constraints at $current);
!system qq($PG_BIN/psql -U $USERNAME -d $DB_NAME).
        qq( -f src/add_constraints.sql > /dev/null) or die $!;
println qq(Constraints are loaded);

# Analyze - update statistics for the all tables in the database
$current = `date`; $current =~ s/\s+$//;
println qq(Updating the statistics at $current);
!system qq($PG_BIN/psql -U $USERNAME -d $DB_NAME -c 'ANALYZE' > /dev/null) or die $!;

# Done
$current = `date`; $current =~ s/\s+$//;
println qq{Done at $current};

$time = time - $^T;
println "Time taken (sec): \t$time";

