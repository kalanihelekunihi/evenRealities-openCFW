/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_MSPI_CONTROL_REMAINING_H
#define OPENCFW_BOOTLOADER_MSPI_CONTROL_REMAINING_H

#include <stdint.h>

/* Recovered request handlers are dispatched to their source providers.
 * Requests outside the outer dispatcher's valid range return status 6. */
uint32_t opencfw_hal_mspi_control_remaining(uint32_t handle,
                                            uint32_t request,
                                            void *config);

#endif
