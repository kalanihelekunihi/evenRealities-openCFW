/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_MSPI_PIOMIXED_CONFIGURE_42488E_H
#define OPEN_CFW_BOOTLOADER_MSPI_PIOMIXED_CONFIGURE_42488E_H

#include <stdint.h>

typedef struct open_cfw_mspi_piomixed_context {
    uint32_t module;
    uint8_t pio_configuration;
} open_cfw_mspi_piomixed_context;

typedef uint32_t (*open_cfw_mspi_piomixed_read_fn)(void *context,
                                                   uint32_t address);
typedef void (*open_cfw_mspi_piomixed_write_fn)(void *context,
                                                uint32_t address,
                                                uint32_t value);
typedef struct open_cfw_mspi_piomixed_ports {
    void *context;
    open_cfw_mspi_piomixed_read_fn read_reg;
    open_cfw_mspi_piomixed_write_fn write_reg;
} open_cfw_mspi_piomixed_ports;

#if defined(__arm__) || defined(__thumb__)
void open_cfw_bootloader_mspi_piomixed_configure_42488e(void);
#else
uint32_t open_cfw_bootloader_mspi_piomixed_configure_42488e(
    const open_cfw_mspi_piomixed_context *instance,
    const open_cfw_mspi_piomixed_ports *ports);
#endif

#endif
