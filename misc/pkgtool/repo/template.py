
#.format(name=, version=, desc=, config=, build=, test=, install=)
mak_template = """#zen-makefile template
# package name: could be set from external-env
__NAME = {pkg.name}
ifeq ($(strip $(__NAME)),)
Z_NAME := $(Z_NAME)
else
Z_NAME = $(__NAME)
endif

# package version: could be set from external-env
__VER = {pkg.version}
ifeq ($(strip $(__VER)),)
Z_VER := $(Z_VER)
else
Z_VER = $(__VER)
endif

# package description
define Z_DESC
{pkg.desc}
endef

# step prepare
define Z_PREPARE
{pkg.st_prepare}
endef

# step config
define Z_CONFIG
{pkg.st_config}
endef

# step build
define Z_BUILD
{pkg.st_build}
endef

# step test
define Z_TEST
{pkg.st_test}
endef

# step install
define Z_INSTALL
{pkg.st_install}
endef

# step unknown
define Z_UNKNOWN
{pkg.st_unknown}
endef


mkfile_dir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(mkfile_dir)common.mak
"""
