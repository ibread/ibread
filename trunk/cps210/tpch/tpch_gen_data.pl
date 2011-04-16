#!/usr/bin/perl -w

###############################################################################
# This script unzips the TPCH installer located in the src directory 
# to the specified directory, compiles the code using the makefile 
# also located in the src directory and generates the data.
#
# This scripts supports the generation of both uniform and skew data.
#
# Usage: perl tpch_gen_data.pl data.properties
#
# Parameters Used: tpch_home, scaling_factor, zipf, 
#                  num_file_splits, first_file_split, last_file_split
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
   print qq(Usage: perl $0 data.properties\n);
   exit(-1);
}

# Get input parameters
%opt = get_options($ARGV[0]);
$TPCH_HOME        = $opt{'tpch_home'};
$SCALING_FACTOR   = $opt{'scaling_factor'};
$NUM_FILE_SPLITS  = $opt{'num_file_splits'};
$FIRST_FILE_SPLIT = $opt{'first_file_split'};
$LAST_FILE_SPLIT  = $opt{'last_file_split'};
$ZIPF             = $opt{'zipf'};

# Error checking
if ($FIRST_FILE_SPLIT < 1)
{
   println qq(Error: first_file_split = $FIRST_FILE_SPLIT: must be >= 1);
}
if ($LAST_FILE_SPLIT > $NUM_FILE_SPLITS)
{
   println qq(Error: last_file_split = $LAST_FILE_SPLIT:).
           qq( must be <= $NUM_FILE_SPLITS);
}

# Output input parameters
!system qq(date) or die $!;
println "Input Parameters:";
println "TPCH home dir: $TPCH_HOME";
println "Scaling factor: $SCALING_FACTOR";
println "Number of file splits: $NUM_FILE_SPLITS";
println "Generate file splits: $FIRST_FILE_SPLIT TO $LAST_FILE_SPLIT";
println "zipf: $ZIPF";
println "";

# Setup the TPCH installation
println "Creating TPCH directory";
!system qq(mkdir -p $TPCH_HOME) or die $!;

println "Copying and unpacking TPCH installation files to $TPCH_HOME";
if ($ZIPF == 0)
{
   !system qq(cp src/tpch_2_9_0.tar.gz $TPCH_HOME) or die $!;
   !system qq(cp src/makefile_2_9_0 $TPCH_HOME/makefile) or die $!;
}
else
{
   !system qq(cp src/tpch_skew_2_8_0.tar.gz $TPCH_HOME) or die $!;
   !system qq(cp src/makefile_2_8_0_skew $TPCH_HOME/makefile) or die $!;
}
!system qq(gunzip $TPCH_HOME/tpch*.gz > /dev/null) or die $!;
!system qq(tar -xvf $TPCH_HOME/tpch*.tar -C $TPCH_HOME > /dev/null) or die $!; 

# Execute make
println "Executing make";
chdir $TPCH_HOME or die $!;
!system qq(make) or die $!;
println "Make completed";
println "";

# Generate the data
$current = `date`; $current =~ s/\s+$//;
println "Starting TPCH data generation at $current";
println "This might take some time depending on the scale factor...";

for ($split = $FIRST_FILE_SPLIT; $split <= $LAST_FILE_SPLIT; $split++)
{
   println "";
   $options = "-vfF -s $SCALING_FACTOR -C $NUM_FILE_SPLITS -S $split"
              . (($ZIPF == 0) ? "" : " -z $ZIPF");
   !system qq(./dbgen $options) or die $!;
}

!system qq(chmod 644 *.tbl*) or die $!;
println "Data generation complete";
println "";

# Done
$current = `date`; $current =~ s/\s+$//;
println qq{Done at $current};

$time = time - $^T;
println "Time taken (sec):\t$time";

