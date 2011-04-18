#!/usr/bin/perl -w
use strict;
#use IO::Handle;
#This script is written for obtaining the important parts of the log.
#created on Mar 11, 2011
#by Yezhou


my $infile_log; # the log file
my $fh_input;
if ( @ARGV < 1 ){
	print "the default setting of the input log files is excecuted:\n";
	print "\tthe log file is: STDIN\n";
	$fh_input = \*STDIN;
}else{
	$infile_log = $ARGV[0];
	open $fh_input, "<$infile_log"
		or die "Can not open file :$infile_log";
}

mkdir ("results", 0777) if (!(-d "./results"));

system "rm ./results/*txt" if (glob "./results/*.txt");
my @output_line =  ("na", "na", "na", "na", "na", "na", "na", "na", "na", 1, "na");  # [0]: time; [1]: client; [2]: server; [3]: operation_type; [4]:file_handler; [5]: uid; [6]: pid; [7]: size; [8]: offset, [9]: record_count, [10]: time_end.
my %comm_record;#hash to store communication records, using client*serer*operation_type as hash key
my @time_record; #array to store the time of the last record of a communication, using time_start for determining print, client*server*operation_type for visiting hash
my $dir = "./results";

#my $counter = 0;

while (my $line = <$fh_input>){
	#print $counter."\n";
	#$counter += 1;
	my $server = 3;#scalar variable for controlling server
	my @client = (4, 5, 6);# array for controlling clients
	my $client_status = 0;
	foreach my $client (@client){#if the transaction is revoked by one of the clients, set status as 1
		if ($line =~ /192\.168\.1\.$client/){
			$client_status = 1;
			last;
		}
	}	
	if ($line =~ /192\.168\.1\.$server/ && ($client_status == 1)){# if the transaction is between the server
#and one of the clients, filter the dumped info
	@output_line =  ("na", "na", "na", "na", "na", "na", "na", "na", "na", 1, "na");
	if($line =~ /\s+access\s+/){
		if( $line =~ /^(.+?) \s+ IP .+ \) \s+ (\S+) \s+ > \s+ (\S+) \: .+? (access) \s+ fh\[(.+)\] .+ $/x){
			@output_line =  ($1, $2, $3, $4, $5, "na", "na", "na", "na", 1, $1);
		}elsif($line =~ /^(.+?) \s+ IP .+ \) \s+ (\S+) \s+ > \s+ (\S+) \: \s+ reply \s+ ok .+? (access) .+? \s+ ids \s+ (\d+) \/ (\d+) \s+ sz \s+ (\d+) .+ $/x){
			@output_line =  ($1, $3, $2, $4, "na", $5, $6, $7, "na", 1, $1);
		}
	}elsif($line =~ /\s+read\s+/){
		if( $line =~ /^(.+?) \s+ IP .+ \) \s+ (\S+) \s+ > \s+ (\S+) \: .+? (read) \s+ fh\[(.+)\] \s+ (\d+) \s* .* \s+ bytes \s+ @ \s+ (\d+) .* $/x){
			@output_line =  ($1, $2, $3, $4, $5, "na", "na", $6, $7, 1, $1);
		}elsif($line =~ /^(.+?) \s+ IP .+ \) \s+ (\S+) \s+ > \s+ (\S+) \: \s+ reply \s+ ok .+? (read) .+? \s+ ids \s+ (\d+) \/ (\d+) \s+ sz \s+ (\d+) .+? $/x){
			@output_line =  ($1, $3, $2, $4, "na", $5, $6, $7, "na", 1, $1);
		}
	}elsif($line =~ /\s+write\s+/){
		if( $line =~ /^(.+?) \s+ IP .+ \) \s+ (\S+) \s+ > \s+ (\S+) \: .+? (write) \s+ fh\[(.+)\] \s+ (\d+) \s* .* \s+ bytes \s+ @ \s+ (\d+) .* $/x){
			@output_line =  ($1, $2, $3, $4, $5, "na", "na", $6, $7, 1, $1);
		}elsif($line =~ /^(.+?) \s+ IP .+ \) \s+ (\S+) \s+ > \s+ (\S+) \: \s+ reply \s+ ok .+? (write) .+? \s+ ids \s+ (\d+) \/ (\d+) \s+ sz \s+ (\d+) .+ $/x){
			@output_line =  ($1, $3, $2, $4, "na", $5, $6, $7, "na", 1, $1);
		}
	}elsif($line =~ /\s+create\s+/){
		if( $line =~ /^(.+?) \s+ IP .+ \) \s+ (\S+) \s+ > \s+ (\S+) \: .+? (create) \s+ fh\[(.+)\] .* \" (.+) \" .* $/x){
			@output_line =  ($1, $2, $3, $4, $5."\:"."$6", "na", "na", "na", "na", 1, $1);
		}elsif($line =~ /^(.+?) \s+ IP .+ \) \s+ (\S+) \s+ > \s+ (\S+) \: \s+ reply \s+ ok .+?
(create) .+? \s+ ids \s+ (\d+) \/ (\d+) \s+ sz \s+ (\d+) .+ $/x){
			@output_line =  ($1, $3, $2, $4, "na", $5, $6, $7, "na", 1, $1);
		}
	}elsif($line =~ /\s+remove\s+/){
		if( $line =~ /^(.+?) \s+ IP .+ \) \s+ (\S+) \s+ > \s+ (\S+) \: .+? (remove) \s+ fh\[(.+)\] .* \" (.+) \" .* $/x){
			@output_line =  ($1, $2, $3, $4, $5."\:"."$6", "na", "na", "na", "na", 1, $1);
		}elsif($line =~ /^(.+?) \s+ IP .+ \) \s+ (\S+) \s+ > \s+ (\S+) \: \s+ reply \s+ ok .+?
(remove) .+? \s+ ids \s+ (\d+) \/ (\d+) \s+ sz \s+ (\d+) .+ $/x){
			@output_line =  ($1, $3, $2, $4, "na", $5, $6, $7, "na", 1, $1);
		}
	}
	if ($output_line[1] ne "na" && ($line =~ /\s+access\s+/ || $line =~ /\s+read\s+/ || $line =~ /\s+write\s+/ || $line =~ /\s+create\s+/ || $line =~ /\s+remove\s+/ )){
		if (!exists( $comm_record{$output_line[1]."*".$output_line[2]."*".$output_line[3]}) ){#using client*serer*operation_type as hash key
			push @time_record, $output_line[10]."*".$output_line[1]."*".$output_line[2]."*".$output_line[3];		#time_end for determining print, client*server*operation_type for visiting hash
			$comm_record{$output_line[1]."*".$output_line[2]."*".$output_line[3]} = [@time_record - 1, @output_line];
		}else{
			#print "I am here\n";
			my $pos = $comm_record{$output_line[1]."*".$output_line[2]."*".$output_line[3]}[0];
			my $length = @time_record - 1;
			if ($comm_record{$output_line[1]."*".$output_line[2]."*".$output_line[3]}[5] ne "na" && $output_line[4] ne "na" && ( $line =~ /\s+ack\s+/ ||($output_line[4] ne $comm_record{$output_line[1]."*".$output_line[2]."*".$output_line[3]}[5]))){
				# if client, server, operation_type keep same, but file handler changes, print and remove the hash element
				if (! &record_update(\@output_line,\@{$comm_record{$output_line[1]."*".$output_line[2]."*".$output_line[3]}})){
					#print "it's ack or new filehandl\n";
					&record_print(@{$comm_record{$output_line[1]."*".$output_line[2]."*".$output_line[3]}});
					delete($comm_record{$output_line[1]."*".$output_line[2]."*".$output_line[3]});
					#print "test here: ",  $comm_record{$output_line[1]."*".$output_line[2]."*".$output_line[3]}[0], $comm_record{$output_line[1]."*".$output_line[2]."*".$output_line[3]}[1], "\n";
					@time_record = (@time_record[0..($pos - 1)], @time_record[($pos + 1)..$length]);
				}else{
					@time_record = (@time_record[0..($pos - 1)], @time_record[($pos + 1)..$length], $output_line[10]."*".$output_line[1]."*".$output_line[2]."*".$output_line[3]);
				}
				&time_array_update($pos, $length, \@time_record,\%comm_record);
			}else{
				#print "I am here to update\n";
				#file handler also keep same, then just update
				@time_record = (@time_record[0..($pos - 1)], @time_record[($pos + 1)..$length], $output_line[10]."*".$output_line[1]."*".$output_line[2]."*".$output_line[3]);
				#print "I begin time_array_update\n";
				&time_array_update($pos, $length, \@time_record,\%comm_record);
				#print "I end time_array_update, being record_update\n";
				$comm_record{$output_line[1]."*".$output_line[2]."*".$output_line[3]}[0] = @time_record - 1;
				&record_update(\@output_line,\@{$comm_record{$output_line[1]."*".$output_line[2]."*".$output_line[3]}});
			}
		}
		foreach my $time_record (@time_record){#printing communications have been waited more than 30 secs
		#	print "$time_record\n";
			my @record_tmp = split /\*/, $time_record;
			$record_tmp[0] =~ /^(\d+)\:(\d+)\:(\d+)\./;
			my $hr_tmp = $1;
			my $min_tmp = $2;
			my $sec_tmp = $3;
			$output_line[0] =~ /^(\d+)\:(\d+)\:(\d+)\./;
			my $hr_now = $1;
			my $min_now = $2;
			my $sec_now = $3;
			my $pos = $comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]}[0];
			my $length = @time_record - 1;
			if(($hr_now * 3600 + $min_now * 60 + $sec_now) - ($hr_tmp * 3600 + $min_tmp * 60 + $sec_tmp) > 30){#printing communications have been waited more than 30 secs
			# 	print $comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]}[0],"--- element 0\t", $comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]}[1],"---element 1\t", $comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]}[2],"----element2\t", $comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]}[3],"--- element 3\t", $comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]}[4],"---element 4\t",$comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]}[5],"--- element 5\n" if ($comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]}[5] ne "na");
			#	print $record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3], "\n";
			#	print "exists hash key\n" if ( exists $comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]});
				&record_print(@{$comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]}}) if ($comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]}[5] ne "na");
				delete($comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]});
				@time_record = (@time_record[0..($pos - 1)], @time_record[($pos + 1)..$length]);
				&time_array_update($pos, $length, \@time_record,\%comm_record);
			}	
		}
	}
	}
}
foreach my $time_record (@time_record){#finally, print the corresponding elements of records still stored in time_record array
	my @record_tmp = split /\*/, $time_record;
	#print "it is final\n"  if ($comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]}[5] ne "na");
	&record_print(@{$comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]}}) if ($comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]}[5] ne "na");
	delete($comm_record{$record_tmp[1]."*".$record_tmp[2]."*".$record_tmp[3]});
}
close($fh_input);

sub time_array_update{#updating the time_record array positions stored in corresponding hash elements
	my ($pos, $length, $time_record,$comm_record) = @_;
	my $pos_tmp = $pos;
	#print "I am in time_array_update\n";
	while ($pos_tmp < $length){
		#print "I am in time_array_update loop $counter \n";
		my @array_tmp = split /\*/, $$time_record[$pos_tmp];
		$$comm_record{$array_tmp[1]."*".$array_tmp[2]."*".$array_tmp[3]}[0] -= 1;
		#$counter += 1;
		$pos_tmp += 1;
	}
}

sub record_update{#updating the record for a communication
	my ($output_line, $comm_record) = @_;
	my $num = 1;
	my $status = 0;
	for my $ele (@$output_line[1..8]) {
		if($$comm_record[$num + 1] eq "na"){
			$status = 1;
			if ($ele ne "na"){
				$$comm_record[$num + 1] = $ele;
			}
		}
		$num += 1;	
	}
	$$comm_record[10] += 1;
	$$comm_record[11] = $$output_line[10];
	return $status;
}

sub record_print{#printing the record for a communication
	my ($num, @output_line_tmp) = @_;
	my $fh = $output_line_tmp[4];
	my @dir_files = glob ("$dir/*.txt");
	my $flag_file_exists = 0;
	foreach my $file (@dir_files){
		if ($file eq "./results/$fh.txt"){
			$flag_file_exists = 1;
			last;
		}
	}
	if ($flag_file_exists == 0){
		open OUT_1, ">./results/$fh.txt";
		select(OUT_1); 
		$| = 1;
		print OUT_1 "time_start\tclient\tserver\toperation_type\tfile_handler\tuid\tpid\tsize\toffset\trecord_count\ttime_end\n";
	}else{
		open OUT_1, ">>./results/$fh.txt";
		select(OUT_1); 
		$| = 1;
	}
	#OUT_1->autoflush(1);
	print ((join "\t", @output_line_tmp), "\n");
	select (STDOUT);
	close (OUT_1);
}
#exit(0);
