;; extensions

;; (require 'dired-x)
;; ;;make dired can copy and delete directory
;; (setq dired-recursive-copies 'top)
;; (setq dired-recursive-deletes 'top)
;; ;; My preferences for default shell commands
;; ;;set the default command to open a file
;; ;;use ! to open that file in a shell
;; (setq dired-guess-shell-alist-user
;;       (list
;;        (list "\\.pl$" "perl")
;;        (list "\\.chm$" "xchm")
;;        (list "\\.rm$" "gmplayer")
;;        (list "\\.rmvb$" "gmplayer")
;;        (list "\\.avi$" "gmplayer")
;;        (list "\\.asf$" "gmplayer")
;;        (list "\\.wmv$" "gmplayer")
;;        (list "\\.htm$" "w3m")
;;        (list "\\.html$" "w3m")
;;        (list "\\.mpg$" "gmplayer")
;;        (list "\\.pdf$" "acroread")
;;        (list "\\.doc$" "ooffice")
;;        (list "\\.ppt$" "ooffice")       
;;        )
;;       )

;; sort function for dired mode, from ann77
;; s s : sort by Size of files
;; s x : sort by eXtension file name of the files
;; s t : sort by Time
;; s n : sort by Name
(add-hook 'dired-mode-hook (lambda ()
  (interactive)
  (make-local-variable  'dired-sort-map)
  (setq dired-sort-map (make-sparse-keymap))
  (define-key dired-mode-map "s" dired-sort-map)
  (define-key dired-sort-map "s"
              '(lambda () "sort by Size"
                (interactive) (dired-sort-other (concat dired-listing-switches "S"))))
  (define-key dired-sort-map "x"
              '(lambda () "sort by eXtension"
                 (interactive) (dired-sort-other (concat dired-listing-switches "X"))))
  (define-key dired-sort-map "t"
              '(lambda () "sort by Time"
                 (interactive) (dired-sort-other (concat dired-listing-switches "t"))))
  (define-key dired-sort-map "n"
              '(lambda () "sort by Name"
                 (interactive) (dired-sort-other (concat dired-listing-switches ""))))))

;; ;; put the directories first at dired mode, from ann77
;; (defun sof/dired-sort ()
;;   "Dired sort hook to list directories first."
;;   (save-excursion
;;     (let (buffer-read-only)
;;       (forward-line 2) ;; beyond dir. header
;;       (sort-regexp-fields t "^.*$" "[ ]*." (point) (point-max))))
;;   (and (featurep 'xemacs)
;;        (fboundp 'dired-insert-set-properties)
;;        (dired-insert-set-properties (point-min) (point-max)))
;;   (set-buffer-modified-p nil))
;; (add-hook 'dired-after-readin-hook 'sof/dired-sort)

;; ;; using M-up to open parent directory, from ann77
;; (add-hook 'dired-mode-hook (lambda ()
;;   (interactive)
;;   (define-key dired-mode-map (kbd "<M-up>" )
;;     'dired-up-directory)
;;   (define-key dired-mode-map (kbd "ESC <up>" ) 'dired-up-directory)))

;; (require 'color-moccur)


;;form Wang Yin's dotemacs
;; the first time using session : M-x desktop-save
(require 'session)
(add-hook 'after-init-hook 'session-initialize) 

(require 'ibuffer)
(global-set-key (kbd "C-x C-b") 'ibuffer)
(setq ibuffer-formats '((mark modified read-only " " (name 32 32) " "
			      (size 6 -1 :right) " " (mode 16 16 :center)
			       " " filename)
			(mark " " (name 16 -1) " " filename))
      ibuffer-elide-long-columns t
      ibuffer-eliding-string "&")

(require 'browse-kill-ring)
(global-set-key [(control c)(k)] 'browse-kill-ring)
(browse-kill-ring-default-keybindings)

;; 查找文件和切换buffer的时候自动提示
(require 'ido)
;; 输入文件名的时候，如果ido在当前目录未找到
;; 会自动在其他目录查找，这里设置延迟为5秒，不然新建文件的时候很烦
(setq ido-auto-merge-delay-time 5)
;; ido默认保存远端文件列表的cache，不会实时更新，需要用C-l
;; 这里设置不要保存cache，实时更新
(setq ido-cache-ftp-work-directory-time 0)
;; 最近工作过的目录会被缓存，最多缓存50条
;; .ido.last里面叫做ido-work-directory-list
(setq ido-max-dir-file-cache 50)
;; 不允许ido缓存以"zhiqiu@"开头的工作目录(不缓存远端目录)
(setq ido-work-directory-list-ignore-regexps '("zhiqiu@"))
;; 全局开启ido-mode
(ido-mode t)

;; ;; 将ido应用于M-x执行命令
;; ;; 这样一来之前的M-x方式要用M-x execute-extended-command来完成
;; (setq ido-execute-command-cache nil)
;; (defun ido-execute-command ()
;;   (interactive)
;;   (call-interactively
;;    (intern
;;     (ido-completing-read
;; 	 "M-x "
;; 	 (progn
;; 	   (unless ido-execute-command-cache
;; 		 (mapatoms (lambda (s)
;; 					 (when (commandp s)
;; 					   (setq ido-execute-command-cache
;; 							 (cons (format "%S" s) ido-execute-command-cache))))))
;; 	   ido-execute-command-cache)))))
;; (add-hook 'ido-setup-hook
;; 		  (lambda ()
;; 			(setq ido-enable-flex-matching t)
;; 			(global-set-key "\M-x" 'ido-execute-command)))

;; 标签浏览的插件
(require 'tabbar)
(tabbar-mode 1)
;;move to previous group
(global-set-key (kbd "s-[") 'tabbar-backward-group)
(global-set-key [s-mouse-4] 'tabbar-backward-group)

;;move to next group
(global-set-key (kbd "s-]") 'tabbar-forward-group)
(global-set-key [s-mouse-5] 'tabbar-forward-group)

;;move to the left tab
(global-set-key (kbd "s-p") 'tabbar-backward)
(global-set-key (kbd "s-P") 'tabbar-backward)
(global-set-key [s-mouse-1] 'tabbar-backward)

;;move to the right tab
(global-set-key (kbd "s-n") 'tabbar-forward)
(global-set-key (kbd "s-N") 'tabbar-forward)
(global-set-key [s-mouse-3] 'tabbar-forward)

;;set the scope of scrolling
(setq tabbar-cycling-scope (quote tabs))

;; control the tab bar scroll left or right
(defun my-tab-scroll-right ()
  (interactive)
  (tabbar-scroll-right '(mouse-1))
  (force-mode-line-update)
  (sit-for 0)
)

(defun my-tab-scroll-left ()
  (interactive)
  (tabbar-scroll-left '(mouse-1))
  (force-mode-line-update)
  (sit-for 0)
)
;; control tab bar move to left or right
(global-set-key (kbd "<s-left>") 'my-tab-scroll-left)
(global-set-key (kbd "<s-right>") 'my-tab-scroll-right)

;;the outlook of the tab
(custom-set-faces
 '(tabbar-default-face
   ((t (:inherit variable-pitch
        :background "gray90"
        :foreground "gray60"
        :height 0.8))))
 '(tabbar-selected-face
   ((t (:inherit tabbar-default-face
        :foreground "darkred"
        :box (:line-width 2 :color "white" :style pressed-button)))))
 '(tabbar-unselected-face
   ((t (:inherit tabbar-default-face
        :foreground "black"
        :box (:line-width 2 :color "white" :style released-button))))))

;;show line number
;;(set-scroll-bar-mode nil)
;;(require 'wb-line-number)
;;(wb-line-number-enable)

;;fold
;; (setq fold-mode-prefix-key "\C-c\C-o")
;; (setq fold-autoclose-other-folds nil)
;; (require 'fold nil t)
;; (when (featurep 'fold)
;;   (add-hook 'find-file-hook 'fold-find-file-hook t))

;; ;;emacs-w3m
;; (add-to-list 'load-path "~/.emacs.d/site-lisp/emacs-w3m")
;; (require 'w3m)
;; ;;(require 'w3m-load) ;;不需要这个包
;; (autoload 'w3m-browse-url "w3m" "Ask a WWW browser to show a URL." t)
;; (setq w3m-command-arguments '("-cookie" "-F"))
;; (setq w3m-use-cookies t)
;; (setq w3m-home-page "http://www.google.com")
;; (setq exec-path (cons "~/bin/" exec-path))
;; (setq browse-url-browser-function 'w3m-browse-url)
;; (setq w3m-default-display-inline-images t)

;; ;;org-mode
;; (add-to-list 'load-path "~/.emacs.d/site-lisp/org")
;; (require 'org-install)
;; (add-to-list 'auto-mode-alist '("\\.org$" . org-mode))
;; (define-key global-map "\C-cl" 'org-store-link)
;; (define-key global-map "\C-ca" 'org-agenda)
;; (add-hook 'org-mode 'turn-on-font-lock)
;; (setq org-log-done t)


;;查字典
;;sdcv mode
(require 'sdcv-mode)
;; i moved the following line to func.el
;; (global-set-key (kbd "C-c s") 'sdcv-search)

;; (require 'template)
;; (template-initialize)
;; (add-to-list 'template-find-file-commands
;;              'ido-exit-minibuffer)

;; show the battery info
(require 'battery)
(battery)
(display-battery-mode t)

;; If not on AC power line, then display battery status on the mode line
(and (require 'battery nil t)
     (functionp 'battery-status-function)
     (or (equal (cdr (assoc ?L (funcall battery-status-function))) "on-line")
	 (display-battery)))


;; ;; 
;; (require 'unicad)


;; add spell-checking mode (flyspell) to text-mode & LaTex-mode
;; exclude spell-checking mode from change-log-mode and log-edit-mode
(dolist (hook '(text-mode-hook LaTeX-mode-hook))
  (add-hook hook (lambda () (flyspell-mode 1))))
(dolist (hook '(change-log-mode-hook log-edit-mode-hook))
  (add-hook hook (lambda () (flyspell-mode -1))))
(setq flyspell-issue-message-flag nil)


;;相同文件名在buffer中自动加前缀文件夹进行区分
(require 'uniquify)  
(setq uniquify-buffer-name-style 'forward)

;;tramp
(require 'tramp)
;; 指定默认方法
(setq tramp-default-method "ssh")
;; 指定默认用户和默认主机
;; (setq tramp-default-user "zhiqiu" tramp-default-host "166.111.214.60")
;; 注意最好设置到500以下
(setq tramp-chunksize 500)
;; 设定tramp文件自动保存在远端目录下
(add-to-list 'backup-directory-alist
			 (cons "." "~/.emacs.d/backup/"))
(setq tramp-backup-directory-alist backup-directory-alist)
;; 自动保存文件
;; (setq auto-save-file-name-transforms "~/.emacs.d/auto-save-list/")
(setq auto-save-file-name-transforms nil)
;; 密码永不过期
(setq password-cache-expiry nil)
;; 
(add-to-list 'tramp-default-proxies-alist
			 '("\\`10\\.1\\.1\\.111\\'"
			   "\\`zhiqiu\\'"
			   "/ssh:zhiqiu@166.111.214.60:"))

;; (add-to-list 'tramp-remote-process-environment "ITG_HOME=/jeda/home/zhiqiu/jtlm2_itg")
;; (add-to-list 'tramp-remote-process-environment "PROTOCOL_HOME=/jeda/home/zhiqiu/cvs/RSG_ITG/examples/osci/simple01/protocol")
;; (add-to-list 'tramp-remote-process-environment "OCPITGM_HOME=/jeda/home/zhiqiu/cvs/OCPITG_Dev/ocpitgm")
;; (add-to-list 'tramp-remote-process-environment "OCP_ITG_HOME=/jeda/home/zhiqiu/OCP_ITG")
;; (add-to-list 'tramp-remote-process-environment "BREAD_TRANS_HOME=/jeda/home/zhiqiu/cvs/RSG_ITG/examples/bread")
;; (add-to-list 'tramp-remote-process-environment "SYSTEMC_HOME=/jeda/opt/rhel3/osci/systemc-2.2.0-gcc323")


;; recent files
(require 'recentf)
(recentf-mode t)