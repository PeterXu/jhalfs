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

#====================

# package introduction
define ZP_INTRO
endef

# package infomation
define ZP_INFO
endef

# package dependencies
define ZP_DEPS
endef

# package contents
define ZP_CONTENT
endef

#====================

# step preproc
define ZS_PREPROC
echo "preproc begin"; \
pwd; \
cd /tmp/; \
pwd; \
uname -a; \
echo $$PATH; \
echo $$(gcc -dumpmachine); \
echo $$; \
echo 123 \
	456 ; \
case $$(uname -m) \
in \
  x86_64) echo 789; \
;; \
esac; \
echo preproc end
endef

# step config
define ZS_CONFIG
endef

# step build
define ZS_BUILD
endef

# step test
define ZS_TEST
endef

# step install
define ZS_INSTALL
endef

# step postproc
define ZS_POSTPROC
endef

# step unknown
define ZS_UNKNOWN
endef

#====================

mkfile_dir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(mkfile_dir)common.mak
