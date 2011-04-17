#!/bin/bash
alias a="alias"
a ll="ls -lh"
a la="ls -a"
a vi="/Applications/MacVim.app/Contents/MacOS/Vim"
a ..="cd .."
a e="emacsclient"
a en="emacsclient -n"
a df="df -h"
a mv="mv -v"
a rm="rm -v"
a jedaftp="lftp wenyong:tryit!@10.1.1.81 -p 2121"
a edaftp="lftp eda_ftp:edaftp404@166.111.68.91:4021"
a jeda="ssh zhiqiu@jedatechnologies-bj.3322.org"
# ssh forwarding
# jeda:1234 -> localhost:22, so commands could be run on locla machine after sshing to jeda
a fdjeda="echo 'jeda:1234 ===> localhost:22';ssh -R 1234:localhost:22 zhiqiu@166.111.214.60"
a fd111="ssh -R 1234:localhost:22 zhiqiu@10.1.1.111"
# localhost:1234 -> 111:22, so I can use /ssh:zhiqiu@localhost#1234:$filename in Emacs
# actually, it's because a bug of tramp, it didn't work fine if you compile/cvs-examine on cascading ssh connection
# so, this is a workaround which change a two-hops ssh connection into 1-hop
a lfd111="echo 'localhost:1234 ===> 111:22';ssh -L 1234:10.1.1.111:22 zhiqiu@166.111.214.60"
a 95="ssh kongzq@192.168.0.95"
a 96="ssh kongzq@192.168.0.96"
a 111="ssh zhiqiu@10.1.1.111"
a 71="ssh zhiqiu@10.1.1.71"
a 55="ssh zhiqiu@10.1.1.55"
a 15="ssh zhiqiu@10.1.1.15"
a cvs="cvs -q"
a c="make clean"
a l="make log"
a m="make"
a d="diff"
a vd="vimdiff *.log golden/"
a up="mv *.log golden/"
a vpn_all="sudo /home/bread/tools/vpn all"
a sign-keys="sudo apt-key adv --recv-keys --keyserver keyserver.ubuntu.com"
#a goto="source $HOME/tools/goto.sh"
a ownself_ftp="lftp ownself:886868@ftp.web7.ey05.cn"

# for sshfs on mac
alias sshfs="/Applications/sshfs/bin/mount_sshfs"
a f95="sshfs kongzq@192.168.0.95:. ~/Remote/95/"
a f96="sshfs kongzq@192.168.0.96:. ~/Remote/96/"
a fjeda="sshfs zhiqiu@166.111.214.60:. ~/Remote/zhiqiu"

# for iphone
a iphone="ssh root@192.168.1.10"
# 43695 端口映射
a ibread="ssh ibread@66.212.19.45 -p 722"

a qqx="ssh root@66.197.135.46"
a ece_x11="xset fp+ ~/Tools/mentor_fonts/ && xset fp rehash && ssh zk11@login.ee.duke.edu"
a ece="ssh zk11@login.ee.duke.edu"

a lmkiller="~/Tools/lmkiller/lmkiller.py"

a server="ssh bread@64.120.204.74"

a os="ssh bingxie@dbc1-03.nicl.cs.duke.edu"
