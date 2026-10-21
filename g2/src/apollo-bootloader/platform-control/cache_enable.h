/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_CACHE_ENABLE_H
#define OPENCFW_BOOT_CACHE_ENABLE_H
#include <stdint.h>
uint32_t opencfw_boot_icache_enable(void);
/* The low byte selects a second set/way clean pass, even when already enabled. */
uint32_t opencfw_boot_dcache_enable(uint32_t clean_after);
#endif
