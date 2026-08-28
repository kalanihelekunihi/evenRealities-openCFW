/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_MSPI_SCHED_HIPRIO_4240AA_H
#define OPEN_CFW_BOOTLOADER_MSPI_SCHED_HIPRIO_4240AA_H

#include <stdint.h>

typedef struct open_cfw_mspi_sched_hiprio_context {
    uint32_t module;
    uint32_t transaction_interrupt;
    uint8_t high_priority_active;
    uint32_t high_priority_entries;
} open_cfw_mspi_sched_hiprio_context;

typedef uint32_t (*open_cfw_mspi_sched_critical_save_fn)(void *context);
typedef void (*open_cfw_mspi_sched_critical_restore_fn)(void *context,
                                                        uint32_t token);
typedef uint32_t (*open_cfw_mspi_sched_operation_fn)(void *context);
typedef uint32_t (*open_cfw_mspi_sched_read_fn)(void *context,
                                                uint32_t address);
typedef void (*open_cfw_mspi_sched_write_fn)(void *context, uint32_t address,
                                             uint32_t value);

typedef struct open_cfw_mspi_sched_hiprio_ports {
    void *context;
    open_cfw_mspi_sched_critical_save_fn critical_save;
    open_cfw_mspi_sched_critical_restore_fn critical_restore;
    open_cfw_mspi_sched_operation_fn command_queue_pause;
    open_cfw_mspi_sched_read_fn read_reg;
    open_cfw_mspi_sched_write_fn write_reg;
    open_cfw_mspi_sched_operation_fn program_dma;
} open_cfw_mspi_sched_hiprio_ports;

#if defined(__arm__) || defined(__thumb__)
void open_cfw_bootloader_mspi_sched_hiprio_4240aa(void);
#else
uint32_t open_cfw_bootloader_mspi_sched_hiprio_4240aa(
    open_cfw_mspi_sched_hiprio_context *instance, uint32_t transaction_count,
    const open_cfw_mspi_sched_hiprio_ports *ports);
#endif

#endif
