/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_MSPI_CONFIGURE_424AF0_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_MSPI_CONFIGURE_424AF0_H

typedef __UINT8_TYPE__ open_cfw_mspi_config_u8;
typedef __UINT32_TYPE__ open_cfw_mspi_config_u32;

#define OPEN_CFW_MSPI_CONFIG_MODULES 4U
#define OPEN_CFW_MSPI_CONFIG_STATE_BYTES 0x8D0U
#define OPEN_CFW_MSPI_CONFIG_REGISTER_BYTES 0xA0U
#define OPEN_CFW_MSPI_CONFIG_SUCCESS 0U
#define OPEN_CFW_MSPI_CONFIG_INVALID_HANDLE 2U
#define OPEN_CFW_MSPI_CONFIG_INVALID_OPERATION 7U

typedef struct open_cfw_mspi_configuration_424af0 {
    open_cfw_mspi_config_u32 tcb_size_words;
    open_cfw_mspi_config_u32 tcb_address;
    open_cfw_mspi_config_u8 clock_on_d4;
} open_cfw_mspi_configuration_424af0;

#if defined(__arm__) || defined(__thumb__)
open_cfw_mspi_config_u32 open_cfw_bootloader_mspi_configure_424af0(
    void *handle, const open_cfw_mspi_configuration_424af0 *configuration);
#else
open_cfw_mspi_config_u32 open_cfw_bootloader_mspi_configure_424af0(
    open_cfw_mspi_config_u8 *handle,
    const open_cfw_mspi_configuration_424af0 *configuration,
    open_cfw_mspi_config_u8
        states[OPEN_CFW_MSPI_CONFIG_MODULES][OPEN_CFW_MSPI_CONFIG_STATE_BYTES],
    open_cfw_mspi_config_u8
        registers[OPEN_CFW_MSPI_CONFIG_MODULES][OPEN_CFW_MSPI_CONFIG_REGISTER_BYTES]);
#endif

#endif
