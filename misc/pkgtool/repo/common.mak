# zen common mak
# zen variables: prefix 'Z_'
# zen targets: prefix 'z_'

ifeq ($(strip $(Z_NAME)),)
Z_NAME = $(shell basename $(CURDIR) | cut -d '-' -f1)
endif

ifeq ($(strip $(Z_VER)),)
Z_VER = $(shell basename $(CURDIR) | cut -d '-' -f2)
ifeq ($(Z_VER),$(shell basename $(CURDIR)))
Z_VER = NO-VERSION
endif
endif

ifeq ($(strip $(ZP_INTRO)),)
ZP_INTRO = The Package <$(Z_NAME)> ...
endif


# check detected version
_BN_VER = $(shell basename $(CURDIR) | cut -d '-' -f2)
ifeq ($(_BN_VER),$(shell basename $(CURDIR)))
_BN_VER = $(Z_VER)
endif
ifneq ($(Z_VER),$(_BN_VER))
$(warning Maybe different versions <$(Z_VER) vs. $(_BN_VER)>???)
endif


none:
	@echo "===== Package $(Z_NAME)/$(Z_VER) ====="
	@echo "Description targets: intro|info|deps|content"
	@echo "Compiling targets:   preproc|config|build|test|install|postproc|unknown"
	@echo

#==================================================

intro:
	$(info ===== Package-Introduction of $(Z_NAME)/$(Z_VER) =====)
	$(info $(ZP_INTRO))
	@echo

info:
	$(info ===== Package-Infomation of $(Z_NAME)/$(Z_VER) =====)
	$(info $(ZP_INFO))
	@echo

deps:
	$(info ===== Package-Dependencies of $(Z_NAME)/$(Z_VER) =====)
	$(info $(ZP_DEPS))
	@echo

content:
	$(info ===== Package-Content of $(Z_NAME)/$(Z_VER) =====)
	$(info $(ZP_CONTENT))
	@echo

#==================================================

define head
 
endef
define crlf


endef
mark = <<newline>>

preproc:
	$(info ===== PreProc of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@$(subst $(mark),,$(ZS_PREPROC))
else
	$(info $(head)$(subst $(mark),$(crlf),$(ZS_PREPROC)))
endif
	@echo

config:
	$(info ===== Config of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@$(subst $(mark),,$(ZS_CONFIG))
else
	$(info $(head)$(subst $(mark),$(crlf),$(ZS_CONFIG)))
endif

build:
	$(info ===== Build of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@$(subst $(mark),,$(ZS_BUILD))
else
	$(info $(head)$(subst $(mark),$(crlf),$(ZS_BUILD)))
endif
	@echo

test:
	$(info ===== Test of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@$(subst $(mark),,$(ZS_TEST))
else
	$(info $(head)$(subst $(mark),$(crlf),$(ZS_TEST)))
endif
	@echo

install:
	$(info ===== Install of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@$(subst $(mark),,$(ZS_INSTALL))
else
	$(info $(head)$(subst $(mark),$(crlf),$(ZS_INSTALL)))
endif
	@echo

postproc:
	$(info ===== PostProc of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@$(subst $(mark),,$(ZS_POSTPROC))
else
	$(info $(head)$(subst $(mark),$(crlf),$(ZS_POSTPROC)))
endif
	@echo

unknown:
	$(info ===== Unknown of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@$(subst $(mark),,$(ZS_UNKNOWN))
else
	$(info $(head)$(subst $(mark),$(crlf),$(ZS_UNKNOWN)))
endif
	@echo

