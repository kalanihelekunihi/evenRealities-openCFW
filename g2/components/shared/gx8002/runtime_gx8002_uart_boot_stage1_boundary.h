/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_UART_BOOT_STAGE1_BOUNDARY_H
#define OPEN_CFW_GX8002_UART_BOOT_STAGE1_BOUNDARY_H

#include "runtime_gx8002_kws_model_boundary.h"

#define OPEN_CFW_GX8002_UART_BOOT_STAGE1_SIZE ((size_t)10240U)
#define OPEN_CFW_GX8002_UART_BOOT_STAGE1_SHA256_HEX \
    "cbbe85a2d60f5bb805dddb45fa2eac1632bdf0ab80665c040c0892c64074133f"

typedef open_cfw_gx8002_segment_provider_fn open_cfw_gx8002_uart_boot_stage1_provider_fn;
typedef open_cfw_gx8002_segment_ports open_cfw_gx8002_uart_boot_stage1_ports;

int32_t open_cfw_gx8002_uart_boot_stage1_load(
    const open_cfw_gx8002_uart_boot_stage1_ports *ports,
    uint8_t *destination,
    size_t capacity);

#endif
