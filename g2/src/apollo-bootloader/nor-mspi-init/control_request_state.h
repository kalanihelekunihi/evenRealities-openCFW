/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_CONTROL_REQUEST_STATE_H
#define OPENCFW_BOOTLOADER_CONTROL_REQUEST_STATE_H
#include <stdint.h>

/* Recoverable request paths 27 and 29 from the locked 0x4251c0 body. */
uint32_t opencfw_hal_mspi_control_state_request(uint32_t handle,
                                               uint32_t request,
                                               void *config);

#endif
