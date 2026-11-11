/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_LOCAL_PROVIDERS_H
#define OPENCFW_BOOT_LOCAL_PROVIDERS_H
#include <stdbool.h>
#include <stdint.h>
/* am_hal_sysctrl_fpu_enable (0x41ac44) */
void opencfw_boot_coprocessor_enable(void);
/* am_hal_sysctrl_fpu_stacking_enable (0x41ac5a) */
void opencfw_boot_fp_lazy_mode(bool lazy);
/* 0x41f9d8: am_hal_delay_us(milliseconds * 1000) */
void opencfw_boot_delay_scaled(uint32_t milliseconds);
/* am_hal_delay_us */
void opencfw_boot_delay_raw(uint32_t microseconds);
#endif
