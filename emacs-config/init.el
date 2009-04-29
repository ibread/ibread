;;加一些自己的目录到load-path之前，以免emacs用自带的同名el文件
(setq load-path (append
		 '("~/.emacs.d/site-lisp"
 		   "~/.emacs.d/site-lisp/cedet/speedbar"
 		   "~/.emacs.d/site-lisp/cedet/common"
		   "~/.emacs.d/site-lisp/cedet/eieio"
		   "~/.emacs.d/site-lisp/cedet/semantic"
		   "~/.emacs.d/site-lisp/cedet/semantic/bovine"
		   "~/.emacs.d/site-lisp/company-mode"
           "~/.emacs.d/site-lisp/ecb"
		 )
		 load-path))

;;字体设置，支持xft
(defun my-default-font()
  (interactive)
  (set-frame-font "Bitstream Vera Sans Mono:pixelsize=16")
  (let ((fontset (frame-parameter nil 'font)))
        (dolist
          (charset '(han symbol cjk-misc bopomofo))
          (set-fontset-font fontset charset '("Microsoft Yahei" . "unicode-bmp")))))

;;新开的frame也应用当前字体设置
(add-to-list 'after-make-frame-functions
             (lambda (new-frame)
               (select-frame new-frame)
               (if window-system
                   (my-default-font))))

(if window-system
    (my-default-font))

;set server-host to be the name of the machine Emacs server will run on
;;(if window-system
;;  (
;;   (setq server-host "bread-laptop")
   ;set server-use-tcp to t
;;   (setq server-use-tcp t)
;;   (server-start)))

(server-start)

(load-file "~/.emacs.d/mycustom.el")
(load-file "~/.emacs.d/elisp.el")
(load-file "~/.emacs.d/program.el")
(load-file "~/.emacs.d/func.el")

;; set custom file to store customization
(setq custom-file "~/.emacs.d/custom.el")
(load custom-file 'noerror)

;;desktopaid的一些设置
(autoload 'dta-hook-up "desktopaid.elc" "Desktop Aid" t)
;;enable the automatic loading and saving of your editing session
(dta-hook-up)

;; (setenv "SYSTEMC_HOME" "/home/bread/software/systemc2.2")
;; (setenv "SYSTEMC_INCLUDE" "$SYSTEMC_HOME/include")
;; (setenv "SYSTEMC_LIB" "$SYSTEMC_HOME/lib-linux")
;; (setenv "ITG_HOME" "/home/bread/jeda/RSG_ITG")
;; (setenv "ITG_ENG" "/home/bread/jeda/RSG_ITG")
;; (setenv "OCPITGM_HOME" "/home/bread/jeda//OCPITG_Dev/ocpitgm")
;; (setenv "PROTOCOL_HOME" "/home/bread/jeda/RSG_ITG/examples/bread")
;; (setenv "BREAD_TRANS_HOME" "/home/bread/jeda/RSG_ITG/examples/bread")


;;; This was installed by package-install.el.
;;; This provides support for the package system and
;;; interfacing with ELPA, the package archive.
;;; Move this code earlier if you want to reference
;;; packages in your .emacs.
;; (when
;; 	(load
;; 	 (expand-file-name "~/.emacs.d/elpa/package.el"))
;;  (package-initialize))

;;配色设置
(require 'color-theme)

;; Emacs - Textmate theme
(require 'tmtheme)
(setq tmtheme-directory "~/.emacs.d/site-lisp/tmthemes")
(tmtheme-scan)

(when window-system
  (color-theme-initialize)
  (color-theme-bread)
  (tmtheme-Merbivore)
)

(add-hook 'after-make-frame-functions
          (lambda (frame)
             (set-variable 'color-theme-is-global nil)
             (select-frame frame)
             (when window-system
			   (color-theme-initialize)
			   (color-theme-bread)
			   (tmtheme-Merbivore)
			   )
))
