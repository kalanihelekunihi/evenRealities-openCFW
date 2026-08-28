/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_MSPI_PROGRAM_DMA_42403E_H
#define OPEN_CFW_BOOTLOADER_MSPI_PROGRAM_DMA_42403E_H

#include <stdint.h>

typedef struct open_cfw_mspi_program_dma_entry {
    uint32_t dma_target_address;
    uint32_t dma_device_address;
    uint32_t dma_total_count;
    uint32_t dma_config;
    void *callback;
    void *callback_context;
} open_cfw_mspi_program_dma_entry;

typedef struct open_cfw_mspi_program_dma_context {
    uint32_t module;
    uint32_t last_hp_index;
    uint32_t max_hp_transactions;
    const open_cfw_mspi_program_dma_entry *hp_transactions;
} open_cfw_mspi_program_dma_context;

typedef uint32_t (*open_cfw_mspi_clock_request_fn)(void *context,
                                                   uint32_t clock_id,
                                                   uint32_t user_id);
typedef void (*open_cfw_mspi_program_dma_write_fn)(void *context,
                                                   uint32_t address,
                                                   uint32_t value);

typedef struct open_cfw_mspi_program_dma_ports {
    void *context;
    open_cfw_mspi_clock_request_fn clock_request;
    open_cfw_mspi_program_dma_write_fn write_reg;
} open_cfw_mspi_program_dma_ports;

#if defined(__arm__) || defined(__thumb__)
void open_cfw_bootloader_mspi_program_dma_42403e(void);
#else
uint32_t open_cfw_bootloader_mspi_program_dma_42403e(
    const open_cfw_mspi_program_dma_context *instance,
    const open_cfw_mspi_program_dma_ports *ports);
#endif

#endif
