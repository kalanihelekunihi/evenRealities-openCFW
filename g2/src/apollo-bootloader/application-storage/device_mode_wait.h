/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_DEVICE_MODE_WAIT_H
#define OPENCFW_BOOT_DEVICE_MODE_WAIT_H

#include <stdint.h>

uint32_t opencfw_boot_device_mode_wait(uint32_t mode, uint32_t event,
                                      uint32_t flags,
                                      volatile uint32_t *result);

#endif
