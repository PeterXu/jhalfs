
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

# step preproc
define Z_PREPROC
{pkg.scripts[preproc]}
endef

# step config
define Z_CONFIG
{pkg.scripts[config]}
endef

# step build
define Z_BUILD
{pkg.scripts[build]}
endef

# step test
define Z_TEST
{pkg.scripts[test]}
endef

# step install
define Z_INSTALL
{pkg.scripts[install]}
endef

# step postproc
define Z_POSTPROC
{pkg.scripts[postproc]}
endef

# step unknown
define Z_UNKNOWN
{pkg.scripts[unknown]}
endef


mkfile_dir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(mkfile_dir)common.mak
"""
