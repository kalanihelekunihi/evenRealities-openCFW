################################################################################
# \file GCC_ARM.mk
#
# \brief
# GCC ARM toolchain configuration
#
################################################################################
# \copyright
# Copyright 2018-2020 Cypress Semiconductor Corporation
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

ifeq ($(WHICHFILE),true)
$(info Processing $(lastword $(MAKEFILE_LIST)))
endif


################################################################################
# Macros
################################################################################

#
# Run ELF2BIN conversion
# $(1) : artifact elf
# $(2) : artifact bin
#
CY_MACRO_ELF2BIN=$(CY_TOOLCHAIN_ELF2BIN) -O binary $1 $2


################################################################################
# Tools
################################################################################

#
# The base path to the GCC cross compilation executables
#
CY_CROSSPATH=$(CY_INTERNAL_TOOL_gcc_BASE)

#
# Build tools
#
CC=$(CY_INTERNAL_TOOL_arm-none-eabi-gcc_EXE)
CXX=$(CY_INTERNAL_TOOL_arm-none-eabi-g++_EXE)
AS=$(CC)
AR=$(CY_INTERNAL_TOOL_arm-none-eabi-ar_EXE)
LD=$(CXX)

#
# Elf to bin conversion tool
#
CY_TOOLCHAIN_ELF2BIN=$(CY_INTERNAL_TOOL_arm-none-eabi-objcopy_EXE)


################################################################################
# Options
################################################################################

#
# DEBUG/NDEBUG selection
#
ifeq ($(CONFIG),Debug)
CY_TOOLCHAIN_DEBUG_FLAG=-DDEBUG
CY_TOOLCHAIN_OPTIMIZATION=-Og
else ifeq ($(CONFIG),Release)
CY_TOOLCHAIN_DEBUG_FLAG=-DNDEBUG
CY_TOOLCHAIN_OPTIMIZATION=-Os
else
CY_TOOLCHAIN_DEBUG_FLAG=
CY_TOOLCHAIN_OPTIMIZATION=
endif

#
# Flags common to compile and link
#
CY_TOOLCHAIN_COMMON_FLAGS=\
	-mthumb\
	-ffunction-sections\
	-fdata-sections\
	-ffat-lto-objects\
	-g\
	-Wall

#
# NOTE: The official NewLib Nano build leaks file buffers when used with reentrant support.
# The ModusToolbox 2.2+ installer bundles a version that fixes this leak that has not yet been
# accepted upstream.
#
CY_TOOLCHAIN_NEWLIBNANO=--specs=nano.specs

#
# CPU core specifics
#
ifeq ($(CORE),CM0)
CY_TOOLCHAIN_FLAGS_CORE=-mcpu=cortex-m0 $(CY_TOOLCHAIN_NEWLIBNANO)
CY_TOOLCHAIN_VFP_FLAGS=
else ifeq ($(CORE),CM0P)
CY_TOOLCHAIN_FLAGS_CORE=-mcpu=cortex-m0plus $(CY_TOOLCHAIN_NEWLIBNANO)
CY_TOOLCHAIN_VFP_FLAGS=
else ifeq ($(CORE),CM4)
CY_TOOLCHAIN_FLAGS_CORE=-mcpu=cortex-m4 $(CY_TOOLCHAIN_NEWLIBNANO)
ifeq ($(VFP_SELECT),hardfp)
CY_TOOLCHAIN_VFP_FLAGS=-mfloat-abi=hard -mfpu=fpv4-sp-d16
else ifeq ($(VFP_SELECT),softfloat)
CY_TOOLCHAIN_VFP_FLAGS=
else
CY_TOOLCHAIN_VFP_FLAGS=-mfloat-abi=softfp -mfpu=fpv4-sp-d16
endif
else ifeq ($(CORE),CM33)
ifeq ($(DSPEXT),no)
CY_TOOLCHAIN_FLAGS_CORE=-mcpu=cortex-m33+nodsp $(CY_TOOLCHAIN_NEWLIBNANO)
else
CY_TOOLCHAIN_FLAGS_CORE=-mcpu=cortex-m33 $(CY_TOOLCHAIN_NEWLIBNANO)
endif
ifeq ($(VFP_SELECT),hardfp)
CY_TOOLCHAIN_VFP_FLAGS=-mfloat-abi=hard -mfpu=fpv5-sp-d16
else ifeq ($(VFP_SELECT),softfloat)
CY_TOOLCHAIN_VFP_FLAGS=
else
CY_TOOLCHAIN_VFP_FLAGS=-mfloat-abi=softfp -mfpu=fpv5-sp-d16
endif
endif

#
# Command line flags for c-files
#
CY_TOOLCHAIN_CFLAGS=\
	-c\
	$(CY_TOOLCHAIN_FLAGS_CORE)\
	$(CY_TOOLCHAIN_OPTIMIZATION)\
	$(CY_TOOLCHAIN_VFP_FLAGS)\
	$(CY_TOOLCHAIN_COMMON_FLAGS)

#
# Command line flags for cpp-files
#
CY_TOOLCHAIN_CXXFLAGS=\
	$(CY_TOOLCHAIN_CFLAGS)\
	-fno-rtti\
	-fno-exceptions

#
# Command line flags for s-files
#
CY_TOOLCHAIN_ASFLAGS=\
	-c\
	$(CY_TOOLCHAIN_FLAGS_CORE)\
	$(CY_TOOLCHAIN_VFP_FLAGS)\
	$(CY_TOOLCHAIN_COMMON_FLAGS)

#
# Command line flags for linking
#
CY_TOOLCHAIN_LDFLAGS=\
	$(CY_TOOLCHAIN_FLAGS_CORE)\
	$(CY_TOOLCHAIN_VFP_FLAGS)\
	$(CY_TOOLCHAIN_COMMON_FLAGS)\
	-Wl,--gc-sections

#
# Command line flags for archiving
#
CY_TOOLCHAIN_ARFLAGS=rvs

#
# Toolchain-specific suffixes
#
CY_TOOLCHAIN_SUFFIX_S=S
CY_TOOLCHAIN_SUFFIX_s=s
CY_TOOLCHAIN_SUFFIX_C=c
CY_TOOLCHAIN_SUFFIX_H=h
CY_TOOLCHAIN_SUFFIX_CPP=cpp
CY_TOOLCHAIN_SUFFIX_HPP=hpp
CY_TOOLCHAIN_SUFFIX_O=o
CY_TOOLCHAIN_SUFFIX_A=a
CY_TOOLCHAIN_SUFFIX_D=d
CY_TOOLCHAIN_SUFFIX_LS=ld
CY_TOOLCHAIN_SUFFIX_MAP=map
CY_TOOLCHAIN_SUFFIX_TARGET=elf
CY_TOOLCHAIN_SUFFIX_PROGRAM=hex
CY_TOOLCHAIN_SUFFIX_ARCHIVE=a

#
# Toolchain specific flags
#
CY_TOOLCHAIN_OUTPUT_OPTION=-o
CY_TOOLCHAIN_MAPFILE=-Wl,-Map,
CY_TOOLCHAIN_STARTGROUP=-Wl,--start-group
CY_TOOLCHAIN_ENDGROUP=-Wl,--end-group
CY_TOOLCHAIN_LSFLAGS=-T
CY_TOOLCHAIN_INCRSPFILE=@
CY_TOOLCHAIN_INCRSPFILE_ASM=@
CY_TOOLCHAIN_OBJRSPFILE=@

#
# Produce a makefile dependency rule for each input file
#
CY_TOOLCHAIN_DEPENDENCIES=-MMD -MP -MF "$(subst .$(CY_TOOLCHAIN_SUFFIX_O),.$(CY_TOOLCHAIN_SUFFIX_D),$@)" -MT "$@"
CY_TOOLCHAIN_EXPLICIT_DEPENDENCIES=-MMD -MP -MF "$$(subst .$(CY_TOOLCHAIN_SUFFIX_O),.$(CY_TOOLCHAIN_SUFFIX_D),$$@)" -MT "$$@"

#
# Additional includes in the compilation process based on this
# toolchain
#
CY_TOOLCHAIN_INCLUDES=

#
# Additional libraries in the link process based on this toolchain
#
CY_TOOLCHAIN_DEFINES=

