/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_NOR_MSPI_DEVICE_CONFIGURE_H
#define OPENCFW_BOOT_NOR_MSPI_DEVICE_CONFIGURE_H
#include <stdint.h>

/* Locked private entry 0x424be4; config points to the stock 24-byte record. */
uint32_t opencfw_hal_mspi_device_configure(uint32_t handle,
                                           const void *config);

#endif
