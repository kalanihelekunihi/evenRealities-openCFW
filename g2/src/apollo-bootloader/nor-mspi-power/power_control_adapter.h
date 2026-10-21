/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_NOR_MSPI_POWER_ADAPTER_H
#define OPENCFW_BOOT_NOR_MSPI_POWER_ADAPTER_H
#include <stdint.h>

/* Stock private call-site ABI at 0x426808. */
uint32_t opencfw_bl_power_control(uint32_t handle, uint32_t operation,
                                  uint32_t retain_state);

#endif
