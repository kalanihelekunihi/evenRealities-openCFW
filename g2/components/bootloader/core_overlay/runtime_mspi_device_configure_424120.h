/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_MSPI_DEVICE_CONFIGURE_424120_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_MSPI_DEVICE_CONFIGURE_424120_H

typedef __UINT8_TYPE__ open_cfw_mspi_dev_u8;
typedef __UINT32_TYPE__ open_cfw_mspi_dev_u32;

typedef struct open_cfw_mspi_device_state {
    open_cfw_mspi_dev_u32 reserved_identity;
    open_cfw_mspi_dev_u32 module;
    open_cfw_mspi_dev_u8 reserved_byte8;
    open_cfw_mspi_dev_u8 clock_on_d4;
    open_cfw_mspi_dev_u8 device_configuration;
} open_cfw_mspi_device_state;

#if defined(__arm__) || defined(__thumb__)
open_cfw_mspi_dev_u32 open_cfw_bootloader_mspi_device_configure_424120(
    const open_cfw_mspi_device_state *instance);
#else
typedef open_cfw_mspi_dev_u32 (*open_cfw_mspi_device_read_fn)(
    void *context, open_cfw_mspi_dev_u32 address);
typedef void (*open_cfw_mspi_device_write_fn)(
    void *context, open_cfw_mspi_dev_u32 address,
    open_cfw_mspi_dev_u32 value);

typedef struct open_cfw_mspi_device_ports {
    void *context;
    open_cfw_mspi_device_read_fn read_reg;
    open_cfw_mspi_device_write_fn write_reg;
} open_cfw_mspi_device_ports;

open_cfw_mspi_dev_u32 open_cfw_bootloader_mspi_device_configure_424120(
    const open_cfw_mspi_device_state *instance,
    const open_cfw_mspi_device_ports *ports);
#endif

#endif
