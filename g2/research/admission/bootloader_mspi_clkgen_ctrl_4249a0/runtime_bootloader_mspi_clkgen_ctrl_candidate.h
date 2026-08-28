/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_MSPI_CLKGEN_CTRL_4249A0_H
#define OPEN_CFW_BOOTLOADER_MSPI_CLKGEN_CTRL_4249A0_H

#include <stdint.h>

typedef uint32_t (*open_cfw_clkgen_critical_save_fn)(void *context);
typedef void (*open_cfw_clkgen_critical_restore_fn)(void *context,
                                                    uint32_t token);
typedef uint32_t (*open_cfw_clkgen_read_fn)(void *context, uint32_t address);
typedef void (*open_cfw_clkgen_write_fn)(void *context, uint32_t address,
                                         uint32_t value);
typedef void (*open_cfw_clkgen_delay_fn)(void *context, uint32_t microseconds);

typedef struct open_cfw_mspi_clkgen_ports {
    void *context;
    open_cfw_clkgen_critical_save_fn critical_save;
    open_cfw_clkgen_critical_restore_fn critical_restore;
    open_cfw_clkgen_read_fn read_reg;
    open_cfw_clkgen_write_fn write_reg;
    open_cfw_clkgen_delay_fn delay_us;
} open_cfw_mspi_clkgen_ports;

#if defined(__arm__) || defined(__thumb__)
void open_cfw_bootloader_mspi_clkgen_ctrl_4249a0(void);
#else
void open_cfw_bootloader_mspi_clkgen_ctrl_4249a0(
    uint32_t module, uint32_t enable, uint32_t configure, uint32_t clock_select,
    const open_cfw_mspi_clkgen_ports *ports);
#endif

#endif
