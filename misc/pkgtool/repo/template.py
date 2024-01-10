
#.format(name=, version=, desc=, config=, build=, test=, install=)
mak_template = """#zen-makefile template
# package name: could be set from external-env
__NAME = {name}
ifeq ($(strip $(__NAME)),)
Z_NAME := $(Z_NAME)
else
Z_NAME = $(__NAME)
endif

# package version: could be set from external-env
__VER = {version}
ifeq ($(strip $(__VER)),)
Z_VER := $(Z_VER)
else
Z_VER = $(__VER)
endif

# package description
define Z_DESC
{desc}
endef

mkfile_dir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(mkfile_dir)common.mak


desc: z_desc

config: z_config
	{config}

build: z_build
	{build}

test: z_test
	{test}

install: z_install
	{install}

"""
