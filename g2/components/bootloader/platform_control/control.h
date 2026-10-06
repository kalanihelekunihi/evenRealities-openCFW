/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_PLATFORM_CONTROL_H
#define OPENCFW_BOOT_PLATFORM_CONTROL_H
#include <stdint.h>
uint32_t opencfw_boot_mram_aligned(uint32_t,const void *,uint32_t,uint32_t);
uint32_t opencfw_boot_mram_dispatch(uint32_t,const void *,uint32_t,uint32_t);
uint32_t opencfw_boot_terminal_mode(uint32_t);
void opencfw_boot_dfu_error_transaction(void);
void opencfw_boot_dfu_runtime_enable(void);
#endif
