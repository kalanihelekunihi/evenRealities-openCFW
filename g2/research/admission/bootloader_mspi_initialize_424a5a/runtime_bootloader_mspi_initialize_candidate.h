/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_MSPI_INITIALIZE_424A5A_H
#define OPEN_CFW_BOOTLOADER_MSPI_INITIALIZE_424A5A_H

#include <stdint.h>

#define OPEN_CFW_MSPI_MODULE_COUNT 4U
#define OPEN_CFW_MSPI_STATE_BYTES 0x8D0U
#define OPEN_CFW_MSPI_STATUS_SUCCESS 0U
#define OPEN_CFW_MSPI_STATUS_OUT_OF_RANGE 5U
#define OPEN_CFW_MSPI_STATUS_INVALID_ARG 6U
#define OPEN_CFW_MSPI_STATUS_INVALID_OPERATION 7U

#if defined(__arm__) || defined(__thumb__)
void open_cfw_bootloader_mspi_initialize_424a5a(void);
#else
uint32_t open_cfw_bootloader_mspi_initialize_424a5a(
    uint32_t module, void **handle,
    uint8_t states[OPEN_CFW_MSPI_MODULE_COUNT][OPEN_CFW_MSPI_STATE_BYTES]);
#endif

#endif
