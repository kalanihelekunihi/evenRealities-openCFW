/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_MSPI_CONFIGURE_424AF0_H
#define OPEN_CFW_BOOTLOADER_MSPI_CONFIGURE_424AF0_H

#include <stdint.h>

#define OPEN_CFW_MSPI_CONFIG_MODULES 4U
#define OPEN_CFW_MSPI_CONFIG_STATE_BYTES 0x8D0U

typedef struct open_cfw_mspi_config {
    uint32_t tcb_size_words;
    uint32_t tcb_address;
    uint8_t clock_on_d4;
} open_cfw_mspi_config;

typedef struct open_cfw_mspi_registers {
    uint32_t dev0axi;
    uint32_t dev0xip;
    uint32_t dev0scrambling;
} open_cfw_mspi_registers;

#if defined(__arm__) || defined(__thumb__)
void open_cfw_bootloader_mspi_configure_424af0(void);
#else
uint32_t open_cfw_bootloader_mspi_configure_424af0(
    uint8_t *handle, const open_cfw_mspi_config *config,
    uint8_t states[OPEN_CFW_MSPI_CONFIG_MODULES][OPEN_CFW_MSPI_CONFIG_STATE_BYTES],
    open_cfw_mspi_registers registers[OPEN_CFW_MSPI_CONFIG_MODULES]);
#endif

#endif
