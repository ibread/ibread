#!/bin/bash

# change default gateway to Paveo's vpn address
change_def_route ()
{
    # get address via ifconfig
    # cisco vpn will be represented as "utun0"
    def_gw=$(ifconfig | grep -A2 utun0 | grep -oE ">.*netmask" | grep -oE "[0-9.]+")

    # if ip address is given as parameter, then check if it's valid
    if echo "$1" | grep -oE "10\.10\.[0-9]{1,3}\.[0-9]{1,3}"; then
        def_gw="$1"
    fi
    route delete default
    route add 0.0.0.0 $def_gw
}

# add route for cn ips, guide them to use previous gateway instead of vpn
# cn_gateway $gateway $ip.lst
cn_gateway ()
{
    if [ $# -lt 2 ]; then
        exit 1
    fi
    gateway="$1"
    iplist="$2"

    echo "Reading ip database..."
    if [ ! -f $iplist ]; then
        echo "Error: No $iplist, plz check it out."
        exit 1
    fi

    # change route table, like this
    #   route -n add 67.202.105.191 $gateway
    echo "Updating route table"
    while read line
    do
        echo "==== delete route entry $line" >> $log
        route -n delete $line >> $log 2>&1
        if [ $only_clear -eq 1 ]; then 
            continue
        fi

        echo "==== add route entry $line" >> $log
        if route -n add $line $gateway >> $log 2>&1; then
            :
            #echo "  Success"
        else
            echo "  Error in entry $line, plz check log"
        fi
    done < $iplist
    echo "Done."

}


# print the help info
print_help()
{
    echo "Route table config script"
    echo "Usages: ./runme.sh [-u | -c | -h]"
    echo " no params: set route table according to chinese ip and extra ip"
    echo " -u: force to update chinese ip database before changing route table"
    echo " -c: do nothing but clear previous added entires"
    echo " -h: display this info"
}

# must be root to execute this script
if [ $EUID -ne 0 ]; then
    echo "You must be root to run this script!"
    echo "Please try again."
    exit 1
fi

# this is flag to indicate if we'll do nothing except clearing route table
only_clear=0

# process arguments
while [ $# -gt 0 ]
do
    case $1 in
        "-u") ./update.py;;
        "-c") only_clear=1;;
        "-h") print_help
                    exit 0;;
        *) ;;
    esac
    shift
done

# check if cn ip database exists
if [ ! -f cn_net_addr.lst ]; then
   ./update.py
fi 

log=route_log # Put your log filename here
# clear the log
> $log

cn_gw=$(head -n1 gateway.txt)
cn_gateway $cn_gw cn_net_addr.lst
cn_gateway $cn_gw extra_ip.lst

#change_def_route
