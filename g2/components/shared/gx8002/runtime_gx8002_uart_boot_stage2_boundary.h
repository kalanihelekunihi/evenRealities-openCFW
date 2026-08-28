/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_UART_BOOT_STAGE2_BOUNDARY_H
#define OPEN_CFW_GX8002_UART_BOOT_STAGE2_BOUNDARY_H

#include "runtime_gx8002_kws_model_boundary.h"

#define OPEN_CFW_GX8002_UART_BOOT_STAGE2_SIZE ((size_t)27964U)
#define OPEN_CFW_GX8002_UART_BOOT_STAGE2_SHA256_HEX \
    "4aacc9e5bf45001bef99785b62302e88bd0b5e6bf4d6186fd7033b1eaeb05b0d"

typedef open_cfw_gx8002_segment_provider_fn open_cfw_gx8002_uart_boot_stage2_provider_fn;
typedef open_cfw_gx8002_segment_ports open_cfw_gx8002_uart_boot_stage2_ports;

int32_t open_cfw_gx8002_uart_boot_stage2_load(
    const open_cfw_gx8002_uart_boot_stage2_ports *ports,
    uint8_t *destination,
    size_t capacity);

#endif
