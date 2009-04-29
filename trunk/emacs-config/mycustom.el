;; 语法高亮
(global-font-lock-mode t)

;; 不用 TAB 来缩进，只用空格。
(setq indent-tabs-mode nil)
(setq default-tab-width 4)
(setq tab-width 4)
;; where M-i stops
(setq tab-stop-list '(4 8 12 16 20 24 28 32 36 40
                        44 48 52 56 60 64 68 72 76 80 84 88 92 96))

;; the column number
(setq default-fill-column 96)

;; set text-mode as default
(setq default-major-mode 'text-mode)
(add-hook 'text-mode-hook 'turn-on-auto-fill) 

;;get rid of toolbar
(tool-bar-mode 0)

;;right scroll bar 
(setq scroll-bar-mode 'right)

;;set default directory
(setq default-directory "~/")

;;平滑滚动，不到屏幕边缘就滚动
(setq scroll-step 1
      scroll-margin 3
	  scroll-conservatively most-positive-fixnum)

;;change yes-or-no-p notification to y-or-n-p
(fset `yes-or-no-p `y-or-n-p)

;; show the column & row number
(setq column-number-mode t)
(setq row-number-mode t)

;; show () match
;; parenthesis – shows the matching paren
;; expression – shows the entire expression enclosed by the paren, and
;; mixed – shows the matching paren if it is visible, and the expression otherwise.
(show-paren-mode t)
(setq show-paren-style 'mixed)

;;show the time
;; (display-time-mode 1)
;; (setq display-time-24hr-format t)
;; (setq display-time-day-and-date t) 
;; (setq display-time-use-mail-icon t)
;; (setq display-time-interval 10)

;;enable the image display
(auto-image-file-mode t)

;;backup directory
(setq backup-directory-alist '(("." . "~/.emacs.d/backup")))
(setq backup-by-copying t)
;;backup vesion control
(setq version-control t) 
(setq kept-new-versions 1) ;; backup the newest version
(setq kept-old-versions 2) ;; backup 2 oldest version(before 1st editing and 2nd editing) 
(setq delete-old-versions t) ;; delete all backup files other than last 3
(setq dired-kept-versions 1)

;;move the mouse when it's near to the cursor
(mouse-avoidance-mode 'animate)

(setq mouse-yank-at-point t);支持中键粘贴 

;; shut down welcome message
(setq inhibit-startup-message t)

;;show where u r now in the title bar
;;(setq frame-title-format "emacs@%b")
;; (setq frame-title-format "%n%F/%b")
;; (setq frame-title-format '(buffer-file-name "%f" ("%b")))

;;;Emacs title bar to reflect file name
(defun frame-title-string ()
  "Return the file name of current buffer, using ~ if under home directory"
  (let
      ((fname (or
               (buffer-file-name (current-buffer))
               (buffer-name))))
    ;;let body
    (when (string-match (getenv "HOME") fname)
      (setq fname (replace-match "~" t t fname))        )
    fname))

;;; Title = 'system-name File: foo.bar'
(setq frame-title-format '("Emacs @ "(:eval (frame-title-string))))

;; 设定光标为短线
;; (setq-default cursor-type 'bar)

;;cursor not flicker
(blink-cursor-mode  -1)

;; mark the end of the file, just like vi
(set-default 'indicate-empty-lines t)
;; 在退出emacs 之前确认是否退出
(setq confirm-kill-emacs 'yes-or-no-p)
;;can copy from emacs to other applications
(when (eq window-system 'x)
  (setq x-select-enable-clipboard t))

;; 设定个人信息
;; (setq user-full-name "Bread")
;; (setq user-mail-address "breaddawson@gmail.com")
(setq user-full-name "Kong Zhiqiu")
(setq user-mail-address "zhiqiu@jedatechnologies.net")

;; 启用文件自动更新到最新改动版本
(global-auto-revert-mode 1)

;; set modeline format
(setq default-mode-line-format 
      (quote
       (#("-" 0 1
          (help-echo "mouse-1: Select (drag to resize)\nmouse-2: Make current window occupy the whole frame\nmouse-3: Remove current window from display"))
        mode-line-mule-info mode-line-modified mode-line-frame-identification
        ;; line position: Bot (117, 26)
        mode-line-position 
        ;; which func mode: [{bread.geta}]
        (which-func-mode 
         ("" which-func-format "-"))
        (vc-mode vc-mode)
        #("  " 0 2
          (help-echo "mouse-1: Select (drag to resize)\nmouse-2: Make current window occupy the whole frame\nmouse-3: Remove current window from display"))
        mode-line-modes
        (global-mode-string
         (#("--" 0 2
            (help-echo "mouse-1: Select (drag to resize)\nmouse-2: Make current window occupy the whole frame\nmouse-3: Remove current window from display"))
          global-mode-string))
        #("-%-" 0 3
          (help-echo "mouse-1: Select (drag to resize)\nmouse-2: Make current window occupy the whole frame\nmouse-3: Remove current window from display"))
        )))


;; Emacs 窗口透明
;; (setf (frame-parameter nil 'alpha) 95)

;; hl-line-mode background color
;; (set-face-background 'hl-line "#827839")


