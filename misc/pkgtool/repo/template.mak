# package name: could be set from external-env
__NAME =
ifeq ($(strip $(__NAME)),)
Z_NAME := $(Z_NAME)
else
Z_NAME = $(__NAME)
endif

# package version: could be set from external-env
__VER =
ifeq ($(strip $(__VER)),)
Z_VER := $(Z_VER)
else
Z_VER = $(__VER)
endif

# package description
define Z_DESC
endef

# step prepare
define Z_PREPARE
echo "prepare begin"; \
pwd; \
uname -a; \
echo prepare end
endef

# step config
define Z_CONFIG
endef

# step build
define Z_BUILD
endef

# step test
define Z_TEST
endef

# step install
define Z_INSTALL
endef

# step uninstall
define Z_UNINSTALL
endef


mkfile_dir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(mkfile_dir)common.mak
