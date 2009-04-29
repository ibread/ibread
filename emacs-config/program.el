;; Load CEDET
(load-file "~/.emacs.d/site-lisp/cedet/common/cedet.el")

;; (require 'speedbar)
(define-key-after (lookup-key global-map [menu-bar tools])
  [speedbar] '("Speedbar". speedbar-frame-mode) [calendar])

;; Enable EDE (Project Management) features
(global-ede-mode t)
;; Enable EDE for a pre-existing C++ project
;; (ede-cpp-root-project "NAME" :file "~/myproject/Makefile")

;; Enabling Semantic (code-parsing, smart completion) features
;; Select one of the following:

;; * This enables the database and idle reparse engines
;; (semantic-load-enable-minimum-features)

;; * This enables some tools useful for coding, such as summary mode
;;   imenu support, and the semantic navigator
(semantic-load-enable-code-helpers)

;; * This enables even more coding tools such as the nascent intellisense mode
;;   decoration mode, and stickyfunc mode (plus regular code helpers)
;; (semantic-load-enable-guady-code-helpers)

;; for using semantic-decoration-all-include-summary
;; (require 'semantic-decorate-include)

;; :( i don't know what this means though
(setq semantic-load-turn-everything-on t)

;; idle-scheduler-idle-time 和 idle-scheduler-work-idle-time的区别
;; 前者不会更新复杂的数据结构和做语法的重新解析，只是会保持当前buffer的更新
;; 以及调用一些函数来完成类似idle-summary的功能
;; 后者则会做语法分析，更新当前文件以及依赖树中所有文件的cache，所以比较废时间
;; 具体的参见和eric的邮件，搜索work-idle-time，已经加星标了
;; Time in seconds of idle before scheduling events
(setq semantic-idle-scheduler-idle-time 2)
;; Time in seconds of idle before scheduling big work.
(setq semantic-idle-scheduler-work-idle-time 10)
;; Maximum size in bytes of buffers automatically reparsed
(setq semantic-idle-scheduler-max-buffer-size 100000)
;; Display of working messages during parse
(setq semantic-idle-scheduler-no-working-message nil)
;; Display definitions and occurences of current variable
(global-semantic-idle-tag-highlight-mode 1)

;; 设置semantic自动完成时调用的tag解析函数; 
(setq semantic-analyze-summary-function 'semantic-format-tag-uml-prototype)
(setq semantic-ia-completion-format-tag-function 'semantic-format-tag-uml-prototype)
(setq semantic-ia-completion-menu-format-tag-function 'semantic-format-tag-uml-prototype)
;; 设置semantic idle summary的tag解析函数
(setq semantic-idle-summary-function 'semantic-format-tag-uml-prototype)

;; ;; 配置Semantic的检索范围:
;; (setq semanticdb-project-roots
;;      (list
;;       (expand-file-name "/")))
;; 设置semantic cache的存放路径
(setq semanticdb-default-save-directory "~/.emacs.d/semantic_cache/")

;; 设置semantic-complete-analyze-inline的显示模式为displayor-ghost
(setq semantic-complete-inline-analyzer-displayor-class (quote semantic-displayor-ghost))

;; 设置C++-mode下semantic的system include路径
(semantic-add-system-include "/home/bread/jeda/RSG_ITG/include/" 'c++-mode)
(semantic-add-system-include "/home/bread/jeda/RSG_ITG/src/" 'c++-mode)
(semantic-add-system-include "/home/bread/jeda/RSG_ITG/examples/bread" 'c++-mode)
(semantic-add-system-include "/home/bread/jeda/RSG_ITG/examples/bread_mq" 'c++-mode)
(semantic-add-system-include "/home/bread/jeda/RSG_ITG/examples/osci/simple01/protocol/" 'c++-mode)
(semantic-add-system-include "/home/bread/software/systemc2.2/include" 'c++-mode)

;; speedbar
(setq speedbar-tag-hierarchy-method '(speedbar-prefix-group-tag-hierarchy speedbar-trim-words-tag-hierarchy speedbar-sort-tag-hierarchy))
;; the list with tag num <= this will not be split into sub-list
(setq speedbar-tag-split-minimum-length 20)
;; two subgroups of tags will be combined if both are less than this
(setq speedbar-tag-regroup-maximum-length 4)

;; 在这里写好像没有什么用
;; ;; auto rebulid directory index imenus
;; (setq semantic-imenu-auto-rebuild-directory-indexes t)
;; ;; how to analyze the tags, i use uml-prototype
;; ;; like this:  foo(i:int):void
;; (setq semantic-imenu-summary-function 'semantic-format-tag-uml-prototype)
;; ;; how to sort the tags
;; (setq semantic-imenu-sort-bucket-function 'semantic-sort-tags-by-name-increasing)

;; 加载ecb, 感觉不太好用所以去掉了
;; (require 'ecb)
;; (require 'ecb-autoloads)
;; (setq ecb-tip-of-the-day nil)
;; (setq ecb-layout-name "left6")

;; 自动将后缀与模式绑定
(setq auto-mode-alist
      (append '(("\\.cpp$" . c++-mode)
		("\\.hpp$" . c++-mode)
		("\\.h$"  . c++-mode)
		("\\.lsp$" . list-mode)
		("\\.scm$" . scheme-mode)
		("\\.pl$" . perl-mode)
		("\\.py$" . python-mode)
		) auto-mode-alist))

;;在单词中间就用自动补全，否则就用TAB
;; "\\>" match the end of the word
;;auto indent, from hhuu
(defun my-indent-or-complete ()
  (interactive)
   (if (looking-at "\\>")
	   (hippie-expand nil)
	 (indent-for-tab-command))
 )

(autoload 'senator-try-expand-semantic "senator")
(setq hippie-expand-try-functions-list
      '(
		senator-try-expand-semantic
		try-expand-dabbrev                  
		try-expand-dabbrev-visible    	  
		try-expand-dabbrev-all-buffers
		try-expand-dabbrev-from-kill
		try-expand-list             ;补全列表
		try-expand-list-all-buffers 
		try-expand-line             ;补全当前行
		try-expand-line-all-buffers
		try-complete-file-name-partially  ;文件名部分匹配
		try-complete-file-name            ;文件名匹配
		try-expand-whole-kill
        try-complete-lisp-symbol-partially ; 部分补全 elisp symbol
        try-complete-lisp-symbol          ; 补全 lisp symbol
	)
)

;; 加载cscope
(add-hook 'c-mode-common-hook
	  '(lambda ()
	    (require 'xcscope)))

(defun my-c-mode-common-hook()
 ;; the number of columns CC Mode indents nested code
 (setq c-basic-offset 4)
 ;; replace tab with spaces
 (setq tab-width 4 indent-tabs-mode nil)
 ;;;hungry-delete and auto-newline
 (c-toggle-auto-hungry-state 1)
 ;;key bindings
 ;;insert a line break suitable to the context, like newline-and-indent, more powerful
 (define-key c-mode-base-map [(return)] 'c-context-line-break)
 (define-key c-mode-base-map [(f7)] 'smart-compile)
 (define-key c-mode-base-map [(f8)] 'ff-get-other-file)
 ;;  (define-key c-mode-base-map [(meta \`)] 'c-indent-command)
 ;; (define-key c-mode-base-map [(control tab)] 'company-expand-common)
 ;; (define-key c-mode-base-map [(control tab)] 'semantic-complete-analyze-inline)
 (define-key c-mode-base-map [(tab)] 'my-indent-or-complete)
 (define-key c-mode-base-map [(control tab)] 'yas/expand)
 (define-key c-mode-base-map [(meta \`)] 'indent-for-tab-command)
 (define-key c-mode-base-map [(meta ?/)] 'semantic-ia-complete-symbol-menu)
 (define-key c-mode-base-map (kbd "C-?") 'semantic-ia-show-summary)
 (define-key c-mode-base-map [(control return)] 'semantic-ia-fast-jump)
 (define-key c-mode-base-map (kbd "C-'") 'pop-global-mark)
 (define-key c-mode-base-map (kbd "C-,") 'hs-hide-block)
 (define-key c-mode-base-map (kbd "C-.") 'hs-show-block)
;;  (define-key c-mode-base-map [(meta ?/)] 'senator-complete-symbol)
;;  (define-key c-mode-base-map [(meta ?/)] 'senator-completion-menu-popup)
 ;; trigger auto complete, will use semantic-complete-analyze-inline by default
 ;; (define-key c-mode-base-map "." 'semantic-complete-self-insert)
 ;; (define-key c-mode-base-map ">" 'semantic-complete-self-insert) 
;;preprocessor
 (setq c-macro-shrink-window-flag t)
 (setq c-macro-preprocessor "cpp")
 (setq c-macro-cppflags " ")
 (setq c-macro-prompt-flag t)
 (setq c-electric-pound-behavior '(alignleft))
;;  (setq hs-minor-mode t)
 (setq abbrev-mode t)
 (c-set-offset 'inline-open 0)
;;  (c-set-offset 'inline-close 0)
 (c-set-offset 'friend '-)
 (c-set-offset 'substatement-open 0)
 (linum-mode 0)
 (c-toggle-auto-newline t) ;;自动换行
;;只在c/c++ mode下调用xref
;;  (defvar xref-current-project nil) ;; can be also "my_project_name"
;;  (defvar xref-key-binding 'local) ;; can be also 'local or 'none
;;  (setq exec-path (cons "~/.emacs.d/site-lisp/xref/" exec-path))
;;  (setq load-path (cons "~/.emacs.d/site-lisp/xref/emacs" load-path))
;;  (load "xrefactory")
)
(add-hook 'c-mode-common-hook 'my-c-mode-common-hook)

;;cpp edit stratigies
(defun my-c++-mode-hook()
 (setq c-basic-offset 4)   ;; 设置缩进为4列
 (setq tab-width 4 indent-tabs-mode nil) ;; 空格代替TAB缩进
 (c-set-style "stroustrup")  ;; set coding style, stroustrup is the author of C++
 (c-set-offset 'inline-open 0) 
 (c-set-offset 'inline-close 0)
 (c-set-offset 'friend 0)
 (c-set-offset 'substatement-open 0)
 (setq c-electric-pound-behavior '(alignleft)) ;; when # is the first character, alignleft
 (add-to-list 'c-hanging-braces-alist '(brace-list-close)) ;; enum COLOR { A,B } 后面的括号前后不自动换行
 (add-to-list 'c-hanging-braces-alist '(substatement-open . (before after))) ;; if (expression){ 括号另起一行
;; (add-to-list 'c-cleanup-list 'empty-defun-braces) ;; class A \n{} 括号}会自动并到上面一行
 (add-to-list 'c-cleanup-list 'defun-close-semi)   ;; 定义后的;会自动并到上面一行定义的尾部
;;  (add-to-list 'c-cleanup-list 'space-before-funcall) ;; fuc_call (a,b) 函数调用和(之间加空格
)
(add-hook 'c++-mode-hook 'my-c++-mode-hook)

(define-abbrev-table 'c++-mode-abbrev-table
   '(("newclass" "" skeleton-new-class 1)))

(define-skeleton skeleton-new-class
 "generate a class" "Class Name:"
  >"\nclass " str
  >"\n{"
  >"\npublic:"
  >"\n" str "()"
  >"\n{"
  >"\n}"
  >"\nvirtual ~" str "()"
  >"\n{"
  >"\n}"
  >"\n" str "(const " str "& other) "
  >"\n{"
  >"\n}"
  >"\n" str "& operator=(const " str "& other)"
  >"\n{"
  >"\nreturn *this;"
  >"\n}"
  >"\nprotected:\n"
  >"\nprivate:"
  >"\n};"
 )

(define-skeleton skeleton-c-mode-mainx
 "generate for () { automatic" nil
 > "int main()"
 > "\n{"
 > "" _ ""
 > "\nreturn 0;"
 > "\n}" >)
(define-abbrev-table 'c++-mode-abbrev-table '(
   ("mainx" "" skeleton-c-mode-mainx 1)
   ))

(define-skeleton skeleton-c-mode-forx
 "generate for () { automatic" nil
 > "for (" _ ")"
 > "\n{"
 > "\n"
 > "}" >)
(define-abbrev-table 'c++-mode-abbrev-table '(
   ("forx" "" skeleton-c-mode-forx 1)
   ))

;------------------
(define-skeleton skeleton-c-mode-whilex
 "generate while () { automatic" nil
 > "while (" _ ") "
 > "\n{"
 > "\n"
 > "\n"
 >  "}" >)
(define-abbrev-table 'c++-mode-abbrev-table '(
   ("whilex" "" skeleton-c-mode-whilex 1)
   ))

;------------------
(define-skeleton skeleton-c-mode-dox
 "generate do { automatic" nil
 > "do"
 > "\n{"
 > "\n"
 > "} while (" _ ");\n" >)
(define-abbrev-table 'c++-mode-abbrev-table '(
   ("dox" "" skeleton-c-mode-dox 1)
   ))

;------------------
(define-skeleton skeleton-c-mode-ifx
 "generate if () { automatic" nil
 > "if (" _ ")"
 > "\n{"
 > "\n"
 > "\n"
 > "}" >)
(define-abbrev-table 'c++-mode-abbrev-table '(
   ("ifx" "" skeleton-c-mode-ifx 1)
   ))

;------------------
(define-skeleton skeleton-c-mode-elsex
 "generate else { automatic" nil
 > "else"
 > "\n{"
 > _ "\n"
 > "}" >)
(define-abbrev-table 'c++-mode-abbrev-table '(
   ("elsex" "" skeleton-c-mode-elsex 1)
   ))

;------------------
(define-skeleton skeleton-c-mode-dbp
 "generate dbp () { automatic" nil
 > "DBP(\"" _ "\");")
(define-abbrev-table 'c++-mode-abbrev-table '(
   ("dbp" "" skeleton-c-mode-dbp 1)
   ))


;; -------------------------
(defun ifdef-0 (beg end)
 (interactive "*r")
 (save-excursion
   (save-restriction
     (narrow-to-region beg end)
     (goto-char (point-max))
     (when (looking-at "^$")
       (delete-blank-lines)
       (backward-delete-char 1))
     (goto-char (point-min))
     (while (looking-at "^$")
       (forward-line 1))
     (if (looking-at "^#if 0")
         (progn
           (delete-region (line-beginning-position)
                          (1+ (line-end-position)))
           (goto-char (point-max))
           (delete-region (line-beginning-position)
                          (point-max)))
       (insert "#if 0\n")
       (goto-char (point-max))
       (insert "\n#endif\n")))))

;;; GUD for C++
;; Add keybindings for gdb to all my c++-buffers
;; (add-hook 'c++-mode-hook
;;          (lambda ()
;;            (local-set-key (kbd "C-<f2>") 'gud-finish)
;;            (local-set-key (kbd "<f4>") 'gud-cont)
;;            (local-set-key (kbd "<f6>") 'gud-break)
;;            (local-set-key (kbd "<f7>") 'gud-next)
;;            (local-set-key (kbd "<f8>") 'gud-step)
;;            (local-set-key (kbd "<f9>") 'gud-tbreak)))

;; code folding
(add-hook 'c-mode-hook 'hs-minor-mode)
(add-hook 'c++-mode-hook 'hs-minor-mode)

;; ;; nxml-mode
;; ;;(require 'rng-auto)
;; (load "~/.emacs.d/site-lisp/nxml-mode-20041004/rng-auto.el")
;; (setq auto-mode-alist
;;       (cons '("\\.\\(xml\\|xsl\\|rng\\|xhtml\\)\\'" . nxml-mode)
;; 	    auto-mode-alist))

;; comment current line
(defun comment-current-line ()
  (interactive)
  (comment-or-uncomment-region (line-beginning-position) (line-end-position)))

;; doxymacs
(require 'doxymacs)
(add-hook 'c-mode-common-hook 'doxymacs-mode)

(defun my-doxymacs-font-lock-hook ()
(if (or (eq major-mode 'c-mode) (eq major-mode 'c++-mode))
   (doxymacs-font-lock)))
(add-hook 'font-lock-mode-hook 'my-doxymacs-font-lock-hook)


;;pair mode
;; (require 'pair-mode)

(defun my-python-mode()
;;     (define-key python-mode-map [return] 'newline-and-indent)
;; 这种定义的方式与上一句那种不同的是当在注释的模式下按回车新的一行是对齐的注释
     (define-key python-mode-map [return] 'comment-indent-new-line)
;;; 下面这行默认的M-;就可以做到
;;;      (define-key python-mode-map "\C-cc" 'comment-or-uncomment-region)
     (interactive)
     (imenu-add-menubar-index) ;; 在菜单条里加入函数列表菜单
     (hs-minor-mode) ;; 打开可以折叠的模式
 ;;;     (custom-set-variables
;;;       '(python-honour-comment-indentation t)
;;;       '(show-paren-mode t)) ;; 括号成对指示
)
(add-hook 'python-mode-hook 'my-python-mode)


;;; 下面这一段的作用是自动添加匹配的括号，但是不好用
;; (add-hook 'python-mode-hook
;; 	  (lambda ()
;; 	    (define-key python-mode-map "\"" 'electric-pair)
;; 	    (define-key python-mode-map "\'" 'electric-pair)
;; 	    (define-key python-mode-map "(" 'electric-pair)
;; 	    (define-key python-mode-map "[" 'electric-pair)
;; 	    (define-key python-mode-map "{" 'electric-pair)))
    
;; (defun electric-pair ()
;;   "Insert character pair without sournding spaces"
;;   (interactive)
;;   (let (parens-require-spaces)
;;     (insert-pair)))

;;智能编译，找不到makefile会自动根据文件类型产生命令
(require 'smart-compile+)


;; (ede-cpp-root-project "not_repeat1" 
;; :file "/home/bread/jeda/regressions/nsca/tests/ITG_Eng/not/repeat/not_repeat1/not_repeat1.cpp"
;; :include-path '( "/include" )
;; :system-include-path '( "/usr/include/c++/4.2/" "/home/bread/jeda/RSG_ITG/include/" "/home/bread/jeda/RSG_ITG/examples/osci/simple01/protocol"))

;; ;; company mode, inline completion front end
;; ;; http://nschum.de/src/emacs/company-mode/
;; (require 'company-mode)
;; (require 'company-bundled-completions)
;; (company-install-bundled-completions-rules)
;; (add-hook 'c++-mode-hook 'company-mode)
;; ;; 090110 这个Bug被fix了，现在不用静态绑定了
;; ;; Emacs的Bug导致在增量显示自动完成列表的时候，M-n和M-p不起作用了, 因此需要重新定义一下
;; (define-key company-mode-map "\M-n" 'company-cycle)
;; (define-key company-mode-map "\M-p" 'company-cycle-backwards)
;; ;; after these many seconds, completions will showe up automatically
;; (setq company-idle-delay nil)
;; ;; only when these many chars have been typed, the completions will show up
;; ;; and this take higher priority on company-idle-delay which means completions will
;; ;; not show up if the chars are too few regardless how many seconds has passed
;; (setq company-complete-on-idle-min-chars 100)
;; ;; after these many seconds, company tooltip window show up where you can use M-p
;; ;; and M-n to navigate between all the completions
;; (setq company-tooltip-delay 1)
;; ;; company-complet-on-edit 3, then completion will automatically show up IMMEDIATELY 
;; ;; after u wrote 3 characters without waiting for company-idle-delay seconds, 
;; ;; for example, there will be a standstill between '#in' and 'clude' since company need
;; ;; to find completions.
;; ;; That's exactly why i set it to nil to turn it off.
;; (setq company-complete-on-edit nil)
;; ;; display 10 completion candidates
;; (setq company-how-many-completions-to-show 10)
;; ;; use psedudo-tootip to display
;; ;; (setq company-display-style 'tootip)

;; company 0.3
;; (autoload 'company-mode "company" nil t)
(require 'company)
(add-hook 'c++-mode-hook 'company-mode)
(add-hook 'emacs-lisp-mode-hook 'company-mode)
(define-key company-mode-map "\M-n" 'company-select-next)
(define-key company-mode-map "\M-p" 'company-select-previous)
(setq company-idle-delay nil)

;; completion ui (http://www.emacswiki.org/emacs/CompletionUI)

;; (require 'completion-ui)
;; (defun semantic-prefix-wrapper ()
;;   "Return prefix at point that Semantic would complete."
;;   (when (semantic-idle-summary-useful-context-p)
;; 	(let ((prefix (semantic-ctxt-current-symbol (point))))
;; 	  (setq prefix (nth (1- (length prefix)) prefix))
;; 	  (set-text-properties 0 (length prefix) nil prefix)
;; 	  prefix)))

;; (defun semantic-completion-wrapper (prefix maxnum)
;;   "Return list of Semantic completions for PREFIX at point.
;;      Optional argument MAXNUM is the maximum number of completions to
;;      return."
;;   (when (semantic-idle-summary-useful-context-p)
;; 	(let* (
;; 		   ;; don't go loading in oodles of header libraries for minor
;; 		   ;; completions if using auto-completion-mode
;; 		   ;; FIXME: don't do this iff the user invoked completion manually
;; 		   (semanticdb-find-default-throttle
;; 			(when (and (featurep 'semanticdb-find)
;; 					   auto-completion-mode)
;; 			  (remq 'unloaded semanticdb-find-default-throttle)))
		   
;; 		   (ctxt (semantic-analyze-current-context))
;; 		   (acomp (semantic-analyze-possible-completions ctxt)))
;; 	  (when (and maxnum (> (length acomp) maxnum))
;; 		(setq acomp (subseq acomp 0 (1- maxnum))))
;; 	  (mapcar 'semantic-tag-name acomp))))

;; (defun completion-setup-semantic ()
;;   "Setup Semantic Completion-UI support."
;;   (interactive)
;;   (setq completion-function 'semantic-completion-wrapper)
;;   (setq completion-prefix-function 'semantic-prefix-wrapper)
;;   (setq auto-completion-override-syntax-alist '((?. . (add word))))
;;   (define-key completion-map "." 'completion-self-insert))


;; yasnippet
(require 'yasnippet)
(yas/initialize)
(yas/load-directory "~/.emacs.d/site-lisp/snippets")

;; configure the face and message shown after collapse codes
(defvar my-hs-overlay-keymap nil "keymap for folding overlay")

(let ((map (make-sparse-keymap)))
  (define-key map [mouse-1] 'hs-show-block)
  (setq my-hs-overlay-keymap map)
  )

(defface protel-folding-overlay
  '((default :inherit region :box (:line-width 3 :color "#2e3436" :style released-button))
    (((class color)) :foreground "red" :background "#2e3436" :italic t))
  "*Font used by folding overlay."
  )

(setq hs-set-up-overlay
      (defun my-display-code-line-counts (ov)
        (when (eq 'code (overlay-get ov 'hs))
          (overlay-put ov 'display
                       (propertize
                        (format " ..... <%d lines> ....."
                                (1- (count-lines (overlay-start ov)
                                             (overlay-end ov))))
						))
		  (overlay-put ov 'face 'protel-folding-overlay)
		  (overlay-put ov 'priority (overlay-end ov))
		  (overlay-put ov 'keymap my-hs-overlay-keymap)
		  (overlay-put ov 'pointer 'hand)
		  )))


