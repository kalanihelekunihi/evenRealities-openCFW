# SPDX-License-Identifier: Apache-2.0

if(CONFIG_MCUBOOT_ACTION_HOOKS)
  zephyr_library()
  zephyr_library_sources(openr1_recovery.c)
endif()
