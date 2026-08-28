/* SPDX-License-Identifier: BSD-3-Clause */
#include "runtime_bootloader_mspi_program_dma_candidate.h"

enum { OPEN_CFW_PROGRAM_DMA_MAX_WRITES = 5 };

typedef struct open_cfw_program_dma_fixture {
    uint32_t clock_status;
    uint32_t clock_id;
    uint32_t user_id;
    uint32_t clock_calls;
    uint32_t write_count;
    uint32_t addresses[OPEN_CFW_PROGRAM_DMA_MAX_WRITES];
    uint32_t values[OPEN_CFW_PROGRAM_DMA_MAX_WRITES];
} open_cfw_program_dma_fixture;

static open_cfw_program_dma_fixture fixture;

static uint32_t clock_request(void *context, uint32_t clock_id,
                              uint32_t user_id)
{
    open_cfw_program_dma_fixture *state = context;
    state->clock_calls++;
    state->clock_id = clock_id;
    state->user_id = user_id;
    return state->clock_status;
}

static void write_reg(void *context, uint32_t address, uint32_t value)
{
    open_cfw_program_dma_fixture *state = context;
    if (state->write_count < OPEN_CFW_PROGRAM_DMA_MAX_WRITES) {
        state->addresses[state->write_count] = address;
        state->values[state->write_count] = value;
    }
    state->write_count++;
}

void open_cfw_test_mspi_program_dma_reset(uint32_t clock_status)
{
    uint32_t index;
    fixture.clock_status = clock_status;
    fixture.clock_id = 0U;
    fixture.user_id = 0U;
    fixture.clock_calls = 0U;
    fixture.write_count = 0U;
    for (index = 0U; index < OPEN_CFW_PROGRAM_DMA_MAX_WRITES; index++) {
        fixture.addresses[index] = 0U;
        fixture.values[index] = 0U;
    }
}

uint32_t open_cfw_test_mspi_program_dma_run(
    uint32_t module, uint32_t last_index, uint32_t maximum,
    const open_cfw_mspi_program_dma_entry *entries)
{
    const open_cfw_mspi_program_dma_context instance = {
        module, last_index, maximum, entries
    };
    const open_cfw_mspi_program_dma_ports ports = {
        &fixture, clock_request, write_reg
    };
    return open_cfw_bootloader_mspi_program_dma_42403e(&instance, &ports);
}

uint32_t open_cfw_test_mspi_program_dma_value(uint32_t selector,
                                              uint32_t index)
{
    if (selector == 0U) return fixture.clock_calls;
    if (selector == 1U) return fixture.clock_id;
    if (selector == 2U) return fixture.user_id;
    if (selector == 3U) return fixture.write_count;
    if (selector == 4U && index < OPEN_CFW_PROGRAM_DMA_MAX_WRITES)
        return fixture.addresses[index];
    if (selector == 5U && index < OPEN_CFW_PROGRAM_DMA_MAX_WRITES)
        return fixture.values[index];
    return 0U;
}
