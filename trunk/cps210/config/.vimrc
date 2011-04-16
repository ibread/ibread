"**********************************************************************
" Bread's VIM Configuration File
" breaddawson@gmail.com
" Aug 4th, 2008
"

" Global Settings
set nocompatible " using Vim setting instead of Vi
set history=100 " the history size
set ruler " display the cursor position at bottom right
set number " show the row number
set hlsearch " highlight searching
set incsearch " incremental search
set showmatch " show the matched brackets
set vb t_vb= "get rid of the beep
"set mouse=a " enable mouse support
set ttymouse=xterm2 "enable mouse support for old version
set selection=exclusive
set selectmode=mouse,key
set fileencodings=utf8,gbk,gb2312,gb18030
colorscheme desert

" For Programming
syntax on "swith the syntax highlight on
"set cindent " cindent mode
"set autoindent "autoindent as the previous line
"set smartindent "smartindent as the previous line
set tabstop=4 "set the width of tab as 4 spaces
set expandtab "expand the tab to spaces
set shiftwidth=4 "set the soft tab width(using >> or <<) as 4

" keymap
" visual mode change default register to X Window Register
vmap Y "*y
" normal mode
" yy => yank to default register
" dd => delete to default register
" p => put from default register
" Y => yank to X Window Register
" D => to X Window Register
" P => put from X Window Register
nmap P "*p
nmap Y "*yy
" nmap D "*dd

" Useful Abbreviate
iab #b /****************************************
iab #e <Space>****************************************/

if has("autocmd")
  " Enable file type detection.
  " Use the default filetype settings, so that mail gets 'tw' set to 72,
  " 'cindent' is on in C files, etc.
  " Also load indent files, to automatically do language-dependent indenting.
"  filetype plugin indent on
  " For all text files set 'textwidth' to 78 characters.
  autocmd FileType text setlocal textwidth=78
  " When editing a file, always jump to the last known cursor position.
  " Don't do it when the position is invalid or when inside an event handler
  " (happens when dropping a file on gvim).
  autocmd BufReadPost *
    \ if line("'\"") > 0 && line("'\"") <= line("$") |
    \   exe "normal g`\"" |
    \ endif
endif " has("autocmd")
