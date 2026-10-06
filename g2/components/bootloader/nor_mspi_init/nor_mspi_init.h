/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_NOR_MSPI_INIT_H
#define OPENCFW_BOOTLOADER_NOR_MSPI_INIT_H

#include <stdint.h>

uint32_t opencfw_provider_420254(uint32_t module,
                                 const void *device_config,
                                 void **current_device_out,
                                 uint32_t reserved);

/* Source implementation of the firmware's internal HAL handle constructor. */
uint32_t opencfw_provider_424a5a(uint32_t module, void **handle_out);

#endif
