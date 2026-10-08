/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_CONTROL_REQUEST_CLOCK_H
#define OPENCFW_BOOTLOADER_CONTROL_REQUEST_CLOCK_H
#include <stdint.h>

/* Request 26 (clock selection) reconstructed from stock dispatch 0x4258ec. */
uint32_t opencfw_hal_mspi_control_clock_request(uint32_t handle,
                                               void *config);

#endif
