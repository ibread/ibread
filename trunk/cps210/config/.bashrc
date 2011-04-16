# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# don't put duplicate lines in the history. See bash(1) for more options
export HISTCONTROL=erasedups
#export HISTTIMEFORMAT="%F %T"

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "$debian_chroot" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
xterm*)
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\W\[\033[00m\]\$ '
    ;;
*)
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
    ;;
esac

# for ls colors
export CLICOLOR=1
export LSCOLORS=GxFxCxDxBxegedabagacad

# Comment in the above and uncomment this below for a color prompt
#PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*|mrxvt*)
    PROMPT_COMMAND='echo -ne "\033]0;${USER}@${HOSTNAME}: ${PWD/$HOME/~}\007"'
    ;;
*)
    ;;
esac

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable color support of ls and also add handy aliases
if [ "$TERM" != "dumb" ]; then
    #eval "`dircolors -b $HOME/.lscolor`"
    alias ls='ls -F'
    #alias dir='ls --color=auto --format=vertical'
    #alias vdir='ls --color=auto --format=long'
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi

#export PATH=$HOME/tools:$HOME/tools/bin:${PATH} 
export PATH=$HOME/Tools/ulipad:$HOME/Tools:${PATH} 
#export LD_LIBRARY_PATH=/usr/lib
export PATH=/home/bread/study/smv/243/bin:${PATH}
export PATH=/home/bread/study/smt/yices-1.0.21/bin:${PATH}
export PATH=/opt/local/bin:${PATH}


export SYSTEMC_HOME="/home/bread/software/systemc2.2"
export SYSTEMC_LIB=$SYSTEMC_HOME/lib-linux
export SYSTEMC_INCLUDE=$SYSTEMC_HOME/include
export TLM_HOME="/home/bread/software/TLM"
export TARGET_ARCH=linux

export ITG_HOME="/home/bread/jeda/RSG_ITG"
export ITG_ENG=$ITG_HOME
export OCPITGM_HOME="/home/bread/jeda//OCPITG_Dev/ocpitgm"

export PROTOCOL_HOME=$ITG_HOME/examples/osci/simple01/protocol
export BREAD_TRANS_HOME=$ITG_HOME/examples/bread

export CVSROOT=:pserver:zhiqiu@166.111.214.60:/cvsroot


export PS1="\[\033[32;1m\]\u@\h \[\033[34;1m\]\W\[\033[0m\]$ "

# for python lib
export PYTHONPATH=/Users/bread/Tools/langconv-0.0.1dev/
export PYTHONPATH=/Users/bread/Tools/mutagen/:${PYTHONPATH}

export LESS_TERMCAP_mb=$'\E[01;31m'
export LESS_TERMCAP_md=$'\E[01;31m'
export LESS_TERMCAP_me=$'\E[0m'
export LESS_TERMCAP_se=$'\E[0m'
export LESS_TERMCAP_so=$'\E[01;44;33m'
export LESS_TERMCAP_ue=$'\E[0m'
export LESS_TERMCAP_us=$'\E[01;32m'

# for adeona
export ADEONADIR=/usr/local/adeona

# for ibus input method
export XMODIFIERS=@im=ibus
export GTK_IM_MODULE=ibus
export QT_IM_MODULE=ibus

# here are some useful functions
if [ -f ~/.bash_funcs ]; then
    . ~/.bash_funcs
fi

# for fink
source /sw/bin/init.sh

export LC_ALL="en_US.UTF-8"
export LANG="en_US.UTF-8"
export SVN_EDITOR="vim"

