
#.format(name=, version=, desc=, config=, build=, test=, install=)
mak_template = """#zen-makefile template
# package name: could be set from external-env
__NAME = {mak.name}
ifeq ($(strip $(__NAME)),)
Z_NAME := $(Z_NAME)
else
Z_NAME = $(__NAME)
endif

# package version: could be set from external-env
__VER = {mak.version}
ifeq ($(strip $(__VER)),)
Z_VER := $(Z_VER)
else
Z_VER = $(__VER)
endif

#====================

# package introduction
define ZP_INTRO
{mak.package[intro]}
endef

# package infomation
define ZP_INFO
{mak.package[info]}
endef

# package dependencies
define ZP_DEPS
{mak.package[deps]}
endef

# package contents
define ZP_CONTENT
{mak.package[content]}
endef

#====================

# step preproc
define ZS_PREPROC
{mak.scripts[preproc]}
endef

# step config
define ZS_CONFIG
{mak.scripts[config]}
endef

# step build
define ZS_BUILD
{mak.scripts[build]}
endef

# step test
define ZS_TEST
{mak.scripts[test]}
endef

# step install
define ZS_INSTALL
{mak.scripts[install]}
endef

# step postproc
define ZS_POSTPROC
{mak.scripts[postproc]}
endef

# step unknown
define ZS_UNKNOWN
{mak.scripts[unknown]}
endef

#====================

mkfile_dir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(mkfile_dir)common.mak
"""
