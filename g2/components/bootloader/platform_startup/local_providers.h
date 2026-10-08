/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_LOCAL_PROVIDERS_H
#define OPENCFW_BOOT_LOCAL_PROVIDERS_H
#include <stdint.h>
void opencfw_boot_coprocessor_enable(void);
void opencfw_boot_fp_lazy_mode(uint32_t mode);
void opencfw_boot_delay_scaled(uint32_t amount);
void opencfw_boot_delay_raw(uint32_t amount);
#endif
