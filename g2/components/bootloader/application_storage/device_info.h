/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_DEVICE_INFO_H
#define OPENCFW_BOOT_DEVICE_INFO_H

#include <stdint.h>

/* Reconstruct the stock 0x41d294 16-word device snapshot. The delay provider
 * is an explicit platform dependency; the range consumer reads word 11. */
void opencfw_boot_device_info_initialize(volatile uint32_t *record);

#endif
