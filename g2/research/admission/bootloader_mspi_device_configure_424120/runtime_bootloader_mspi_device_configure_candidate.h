/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_MSPI_DEVICE_CONFIGURE_424120_H
#define OPEN_CFW_BOOTLOADER_MSPI_DEVICE_CONFIGURE_424120_H

#include <stdint.h>

typedef struct open_cfw_mspi_device_configure_context {
    uint32_t module;
    uint8_t clock_on_d4;
    uint8_t device_configuration;
} open_cfw_mspi_device_configure_context;

typedef uint32_t (*open_cfw_mspi_device_read_fn)(void *context,
                                                 uint32_t address);
typedef void (*open_cfw_mspi_device_write_fn)(void *context, uint32_t address,
                                              uint32_t value);

typedef struct open_cfw_mspi_device_configure_ports {
    void *context;
    open_cfw_mspi_device_read_fn read_reg;
    open_cfw_mspi_device_write_fn write_reg;
} open_cfw_mspi_device_configure_ports;

#if defined(__arm__) || defined(__thumb__)
void open_cfw_bootloader_mspi_device_configure_424120(void);
#else
uint32_t open_cfw_bootloader_mspi_device_configure_424120(
    const open_cfw_mspi_device_configure_context *instance,
    const open_cfw_mspi_device_configure_ports *ports);
#endif

#endif
