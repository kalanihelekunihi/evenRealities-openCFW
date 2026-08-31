/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_MSPI_INITIALIZE_424A5A_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_MSPI_INITIALIZE_424A5A_H

typedef __UINT8_TYPE__ open_cfw_mspi_init_u8;
typedef __UINT32_TYPE__ open_cfw_mspi_init_u32;

#define OPEN_CFW_MSPI_INIT_MODULE_COUNT 4U
#define OPEN_CFW_MSPI_INIT_STATE_BYTES 0x8D0U
#define OPEN_CFW_MSPI_INIT_SUCCESS 0U
#define OPEN_CFW_MSPI_INIT_OUT_OF_RANGE 5U
#define OPEN_CFW_MSPI_INIT_INVALID_ARG 6U
#define OPEN_CFW_MSPI_INIT_INVALID_OPERATION 7U

#if defined(__arm__) || defined(__thumb__)
open_cfw_mspi_init_u32 open_cfw_bootloader_mspi_initialize_424a5a(
    open_cfw_mspi_init_u32 module, void **handle);
#else
open_cfw_mspi_init_u32 open_cfw_bootloader_mspi_initialize_424a5a(
    open_cfw_mspi_init_u32 module, void **handle,
    open_cfw_mspi_init_u8
        states[OPEN_CFW_MSPI_INIT_MODULE_COUNT][OPEN_CFW_MSPI_INIT_STATE_BYTES]);
#endif

#endif
