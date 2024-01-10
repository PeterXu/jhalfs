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

ifeq ($(strip $(Z_DESC)),)
Z_DESC = The Package <$(Z_NAME)> ...
endif


# check detected version
_BN_VER = $(shell basename $(CURDIR) | cut -d '-' -f2)
ifeq ($(_BN_VER),$(shell basename $(CURDIR)))
_BN_VER = NO-VERSION
endif
ifneq ($(Z_VER),$(_BN_VER))
$(warning Maybe different versions <$(Z_VER) vs. $(_BN_VER)>???)
endif


z_none:
	@echo

z_desc:
	$(info ===== Description of $(Z_NAME)/$(Z_VER) =====)
	$(info $(Z_DESC))
	@echo

z_config:
	$(info ===== Config of $(Z_NAME)/$(Z_VER) =====)
	@echo

z_build:
	$(info ===== Build of $(Z_NAME)/$(Z_VER) =====)
	@echo

z_test:
	$(info ===== Test of $(Z_NAME)/$(Z_VER) =====)
	@echo

z_install:
	$(info ===== Install of $(Z_NAME)/$(Z_VER) =====)
	@echo

