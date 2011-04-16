package GetOptions;
use 5.8.4;
our @EXPORT_OK=qw(get_options println);
use Exporter;
our @ISA = qw(Exporter);

# Method: get_options
# Input: a file name residing in the parent directory
# Parses a key-value file (key-values separated by =)
# and returns a map with the options
sub get_options
{
    my %opt = ();
    open my $in, qq($_[0]) or die qq($!: $_[0]);
    while($line = <$in>)
    {
        $line =~ s/(.*)#.*/$1/; #Ignore comments
        if ($line =~ m/(\S+)\s*=\s*(\S.*)/)
        {
            $key = $1;
            $value = $2;
            $value =~ s/\s*$//;
            $opt{$key}=$value;
        }
    }
    close $in;
    return %opt;
}

# Simple method to print new lines
sub println {
    local $\ = "\n";
    print @_;
}

1;
