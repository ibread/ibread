;;some funcions and some key bindings

(defun my-insert-date ()
  (interactive) 
  (insert (format-time-string "%a %b %d %H:%M:%S %Y" (current-time))))
(global-set-key (kbd "C-c m d") 'my-insert-date)

(defun global-set-keys (&rest keycommands)
  "Register keys to commands."
  (while keycommands
    (let ((key (car keycommands))
          (command (cadr keycommands)))
      (eval `(global-set-key (kbd ,key) (quote ,command))))
    (setq keycommands (cdr (cdr keycommands)))))

(global-set-keys
 "M-g"            'goto-line                                 ;; default useless
 ;; This command is disabled since in many modes, such as ibuffer, c-o is used to open a file
 "s-o"            'other-window                              ;; handy
 "<f1>"           'shell                                     ;; run a shell in current directory
 "<f2>"           'set-mark-command                          ;; handy
 "<f3>"           'dired                                     ;; handy
 "<f4>"           'ansi-term
 "<f5>"           'info
 "<f6>"           '(lambda ()
					 (interactive)
					 (insert (format-time-string "%F %T")))  ;; insert current time
 "<f7>"           'smart-compile
 "<f8>"           'run-scheme                                ;; run scheme
 "<f9>"           'grep
 ;;  "<f10>"          'w3m                                       ;; explorer
 "<f10>"          'cvs-examine
 "<f11>"          'make-directory                            ;; handy
 "<f12>"          '(lambda ()
					 (interactive)
					 (server-edit)
					 (suspend-frame))         ;; when finish edit a file from terminal, suspend current frame
 "C-%"            'match-paren                ;; match paren, use C-% jump to the matched paren
 "M-s"            'speedbar-get-focus         ;; speed bar get focud
 "C-c t"          'template-expand-template   ;; expand template
 "s-k"            '(lambda ()
					 (interactive)
					 (kill-buffer (current-buffer))) ;; kill current buffer
 "C-;"            'comment-current-line
 "M-<up>"           'enlarge-window
 "M-<down>"         'shrink-window
 "s-i"            'zwl-copy-current-line
 "s-m"            'ecb-goto-window-methods 
 "C-c a"          'wy-go-to-char ;go to the specified char
 "C-c c"          'ispell-word ;spell-checking
 "C-c r"          'revert-buffer ;revert current buffer
 "C-c d"          'sdcv-search
 "C-x C-r"		  'eval-region
 )

;; (global-set-key '[M-up] 'enlarge-window)
;; (global-set-key (kbd, "<M-up>") 'enlarge-window

;;use ansi color in shell mode
(setq explicit-shell-file-name "/bin/bash")
(autoload 'ansi-color-for-comint-mode-on "ansi-color" nil t)
(add-hook 'shell-mode-hook 'ansi-color-for-comint-mode-on)
;; set the color of ansi-term
(setq ansi-term-color-vector [unspecified "#262626" "#7fffd4" "#98fb98" "#fbfaa2"
                                          "#87ceeb" "#afeeee" "#40e0d0" "#bebebe"])

;; comment current line
(defun comment-current-line()
  (interactive)
  (comment-or-uncomment-region (line-beginning-position) (line-end-position)))


;; from an77, when exit shell, kill the buffer
(add-hook 'shell-mode-hook 'wcy-shell-mode-hook-func)

(defun wcy-shell-mode-hook-func  ()
  (set-process-sentinel (get-buffer-process (current-buffer))
						#'wcy-shell-mode-kill-buffer-on-exit)
  )
(defun wcy-shell-mode-kill-buffer-on-exit (process state)
  (message "%s" state)
  (if (or
       (string-match "exited abnormally with code.*" state)
       (string-match "finished" state))
      (kill-buffer (current-buffer))))

(defun wy-go-to-char (n char)
  "Move forward to Nth occurence of CHAR.
Typing `wy-go-to-char-key' again will move forwad to the next Nth
occurence of CHAR."
  (interactive "p\ncGo to char: ")
  (search-forward (string char) nil nil n)
  (while (char-equal (read-char)
					 char)
    (search-forward (string char) nil nil n))
  (setq unread-command-events (list last-input-event)))

;; (define-key global-map (kbd "C-c a") 'wy-go-to-char)


;; find the match paren
(defun match-paren (arg)
  "Go to the matching paren if on a paren; otherwise insert %."
  (interactive "p")
  (cond ((looking-at "\\s\(") (forward-list 1) (backward-char 1))
        ((looking-at "\\s\)") (forward-char 1) (backward-list 1))
        (t (self-insert-command (or arg 1)))))

;;clear the ^M of dos files
(defun dos-unix () (interactive)
  (goto-char (point-min))
  (while (search-forward "\r" nil t) (replace-match "")))
(defun unix-dos () (interactive)
  (goto-char (point-min))
  (while (search-forward "\n" nil t) (replace-match "\r\n")))

;; set the grep common 
(setq grep-command "grep -nH -R . -e ")

;;appt
(setq appt-issue-message t)

;;copy current line
(defun zwl-copy-current-line ()
  "Copy current line to kill-ring"
  (interactive)
  (kill-ring-save (line-beginning-position) (line-end-position)))

;; (require 'sr-speedbar)
;; (global-set-key [(super ?s)] 'sr-speedbar-toggle) 

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; View Mode Settings
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; toggle on view mode automatically when buffer is toggled to read only
;; (setq view-read-only t)

;; (defun view-mode-keybinding-hook ()
;;   (define-key view-mode-map "h" 'backward-char)
;;   (define-key view-mode-map "l" 'forward-char)cpp
;;   (define-key view-mode-map "j" 'next-line)
;;   (define-key view-mode-map "n" 'next-line)
;;   (define-key view-mode-map "k" 'previous-line)
;;   (define-key view-mode-map "p" 'previous-line)
;;   )

;; (add-hook 'view-mode-hook 'view-mode-keybinding-hook)


(defun recursive-count-words (region-end)
  "Number of words between point and REGION-END."
;;; 1. do-again-test
  (if (and (< (point) region-end)
           (re-search-forward "\\w+\\W*" region-end t))
;;; 2. then-part: the recursive call
      (1+ (recursive-count-words region-end))
;;; 3. else-part
    0))

;;; Recursive version
(defun count-words-region (beginning end)
  "Print number of words in the region.

Words are defined as at least one word-constituent
character followed by at least one character that is
not a word-constituent.  The buffer's syntax table
determines which characters these are."
  (interactive "r")
  (message "Counting words in region ... ")
  (save-excursion
    (goto-char beginning)
    (let ((count (recursive-count-words end)))
      (cond ((zerop count)
             (message
              "The region does NOT have any words."))
            ((= 1 count)
             (message "The region has 1 word."))
            (t
             (message
              "The region has %d words." count))))))

;; ---------------------------------------------------
;; 临时记号
;; 有时你需要跳到另一个文件进行一些操作，然后很快的跳回来。你当然可以使用
;; bookmark 或者寄存器。但是这些实在是太慢了。当你按 C-' 时就做了一个记号
;; 然后你可以到别处，按 C-; 就可以在这两点之间来回跳转了
(global-set-key (kbd "C-c b") 'ska-point-to-register)
(global-set-key (kbd "C-c j") 'ska-jump-to-register)
(defun ska-point-to-register()
  "Store cursorposition _fast_ in a register.
Use ska-jump-to-register to jump back to the stored
position."
  (interactive)
  (setq zmacs-region-stays t)
  (point-to-register 8))

(defun ska-jump-to-register()
  "Switches between current cursorposition and position
that was stored with ska-point-to-register."
  (interactive)
  (setq zmacs-region-stays t)
  (let ((tmp (point-marker)))
    (jump-to-register 8)
    (set-register 8 tmp)))

(defun iwb ()
  "indent whole buffer"
  (interactive)
  (delete-trailing-whitespace)
  (indent-region (point-min) (point-max) nil)
  (untabify (point-min) (point-max)))


;;跟ecb有关的键位绑定
;; C-c . r 刷新methods窗口
;; C-c . s		 ecb-windows-sync	将所有内容跟当前buffer同步，其实就是刷新
;; C-c . gm	 ecb-goto-window-methods
;; C-c . gh	 ecb-goto-window-history
;; C-c . g1	 ecb-goto-window-edit1
