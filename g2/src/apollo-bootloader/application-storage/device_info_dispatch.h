/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_DEVICE_INFO_DISPATCH_H
#define OPENCFW_BOOT_DEVICE_INFO_DISPATCH_H

#include <stdint.h>

uint32_t opencfw_boot_device_info_query(uint32_t selector,
                                        volatile uint32_t *record);

#endif
