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
echo "preproc begin"; <<newline>>\
pwd; <<newline>>\
cd /tmp/; <<newline>>\
pwd; <<newline>>\
uname -a; <<newline>>\
echo $$PATH; <<newline>>\
echo $$(gcc -dumpmachine); <<newline>>\
echo $$; <<newline>>\
echo 123 \
	456; <<newline>>\
case $$(uname -m) <<newline>>\
   in <<newline>>\
   x86_64) <<newline>>\
	 echo 789; <<newline>>\
	;; <<newline>>\
esac; <<newline>>\
if [ 1 -eq 1 ]; then <<newline>>\
	 echo 321; <<newline>>\
fi; <<newline>>\
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
