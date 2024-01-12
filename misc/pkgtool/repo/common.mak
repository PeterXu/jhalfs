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
_BN_VER = $(Z_VER)
endif
ifneq ($(Z_VER),$(_BN_VER))
$(warning Maybe different versions <$(Z_VER) vs. $(_BN_VER)>???)
endif


none:
	@echo

desc:
	$(info ===== Description of $(Z_NAME)/$(Z_VER) =====)
	$(info $(Z_DESC))
	@echo

prepare:
	$(info ===== Prepare of $(Z_NAME)/$(Z_VER) =====)
	@echo ">";$(Z_PREPARE)

config:
	$(info ===== Config of $(Z_NAME)/$(Z_VER) =====)
	@echo ">";$(Z_CONFIG)
	@echo

build:
	$(info ===== Build of $(Z_NAME)/$(Z_VER) =====)
	@echo ">";$(Z_BUILD)
	@echo

test:
	$(info ===== Test of $(Z_NAME)/$(Z_VER) =====)
	@echo ">";$(Z_TEST)
	@echo

install:
	$(info ===== Install of $(Z_NAME)/$(Z_VER) =====)
	@echo ">";$(Z_INSTALL)
	@echo

unknown:
	$(info ===== Unknown of $(Z_NAME)/$(Z_VER) =====)
	@echo ">";$(Z_UNKNOWN)
	@echo

