/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_MSPI_CQ_PAUSE_423FB8_H
#define OPEN_CFW_BOOTLOADER_MSPI_CQ_PAUSE_423FB8_H

#include <stdint.h>

typedef uint32_t (*open_cfw_mspi_cq_pause_read_fn)(void *context,
                                                   uint32_t address);
typedef void (*open_cfw_mspi_cq_pause_write_fn)(void *context,
                                                uint32_t address,
                                                uint32_t value);
typedef void (*open_cfw_mspi_cq_pause_delay_fn)(void *context,
                                                uint32_t microseconds);
typedef uint32_t (*open_cfw_mspi_cq_pause_status_fn)(
    void *context, uint32_t timeout, uint32_t address, uint32_t mask,
    uint32_t value, uint32_t not_equal);

typedef struct open_cfw_mspi_cq_pause_context {
    uint32_t reserved;
    uint32_t module;
} open_cfw_mspi_cq_pause_context;

typedef struct open_cfw_mspi_cq_pause_ports {
    void *context;
    open_cfw_mspi_cq_pause_read_fn read_reg;
    open_cfw_mspi_cq_pause_write_fn write_reg;
    open_cfw_mspi_cq_pause_delay_fn delay_us;
    open_cfw_mspi_cq_pause_status_fn status_check;
} open_cfw_mspi_cq_pause_ports;

#if defined(__arm__) || defined(__thumb__)
void open_cfw_bootloader_mspi_cq_pause_423fb8(void);
#else
uint32_t open_cfw_bootloader_mspi_cq_pause_423fb8(
    const open_cfw_mspi_cq_pause_context *instance,
    const open_cfw_mspi_cq_pause_ports *ports);
#endif

#endif
