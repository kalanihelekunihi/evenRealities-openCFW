/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_POWER_DOMAINS_H
#define OPENCFW_BOOT_POWER_DOMAINS_H
#include <stdint.h>
uint32_t opencfw_bl_mspi_mode_enter(uint32_t selector);
uint32_t opencfw_bl_mspi_mode_leave(uint32_t selector);
uint32_t opencfw_boot_power_release_needed(uint32_t selector);
uint32_t opencfw_boot_power_callback(uint32_t selector,uint32_t enabled,void *value);
uint32_t opencfw_boot_power_hook_begin(void);
uint32_t opencfw_boot_power_hook_end(void);
#endif
