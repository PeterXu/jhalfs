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

define crlf


endef

preproc:
	$(info ===== PreProc of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@echo ">";$(ZS_PREPROC)
else
	$(info $(subst ; ,$(crlf),$(ZS_PREPROC)))
endif
	@echo

config:
	$(info ===== Config of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@echo ">";$(ZS_CONFIG)
else
	$(info $(subst ; ,$(crlf),$(ZS_CONFIG)))
endif

build:
	$(info ===== Build of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@echo ">";$(ZS_BUILD)
else
	$(info $(subst ; ,$(crlf),$(ZS_BUILD)))
endif
	@echo

test:
	$(info ===== Test of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@echo ">";$(ZS_TEST)
else
	$(info $(subst ; ,$(crlf),$(ZS_TEST)))
endif
	@echo

install:
	$(info ===== Install of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@echo ">";$(ZS_INSTALL)
else
	$(info $(subst ; ,$(crlf),$(ZS_INSTALL)))
endif
	@echo

postproc:
	$(info ===== PostProc of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@echo ">";$(ZS_POSTPROC)
else
	$(info $(subst ; ,$(crlf),$(ZS_POSTPROC)))
endif
	@echo

unknown:
	$(info ===== Unknown of $(Z_NAME)/$(Z_VER) =====)
ifeq ($(Z_EXEC),1)
	@echo ">";$(ZS_UNKNOWN)
else
	$(info $(subst ; ,$(crlf),$(ZS_UNKNOWN)))
endif
	@echo

