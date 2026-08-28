/* SPDX-License-Identifier: BSD-3-Clause */
#include "runtime_bootloader_mspi_sched_hiprio_candidate.h"

enum { OPEN_CFW_SCHED_MAX_EVENTS = 8 };

typedef struct open_cfw_sched_fixture {
    uint32_t critical_token;
    uint32_t pause_status;
    uint32_t program_status;
    uint32_t read_value;
    uint32_t critical_save_calls;
    uint32_t critical_restore_calls;
    uint32_t restored_token;
    uint32_t pause_calls;
    uint32_t read_calls;
    uint32_t read_address;
    uint32_t write_calls;
    uint32_t write_addresses[2];
    uint32_t write_values[2];
    uint32_t program_calls;
    uint32_t event_count;
    uint32_t events[OPEN_CFW_SCHED_MAX_EVENTS];
} open_cfw_sched_fixture;

static open_cfw_sched_fixture fixture;

static void record(uint32_t event)
{
    if (fixture.event_count < OPEN_CFW_SCHED_MAX_EVENTS) {
        fixture.events[fixture.event_count] = event;
    }
    fixture.event_count++;
}

static uint32_t critical_save(void *context)
{
    open_cfw_sched_fixture *state = context;
    state->critical_save_calls++;
    record(1U);
    return state->critical_token;
}

static void critical_restore(void *context, uint32_t token)
{
    open_cfw_sched_fixture *state = context;
    state->critical_restore_calls++;
    state->restored_token = token;
    record(2U);
}

static uint32_t command_queue_pause(void *context)
{
    open_cfw_sched_fixture *state = context;
    state->pause_calls++;
    record(3U);
    return state->pause_status;
}

static uint32_t read_reg(void *context, uint32_t address)
{
    open_cfw_sched_fixture *state = context;
    state->read_calls++;
    state->read_address = address;
    record(5U);
    return state->read_value;
}

static void write_reg(void *context, uint32_t address, uint32_t value)
{
    open_cfw_sched_fixture *state = context;
    if (state->write_calls < 2U) {
        state->write_addresses[state->write_calls] = address;
        state->write_values[state->write_calls] = value;
    }
    state->write_calls++;
    record(state->write_calls == 1U ? 4U : 6U);
}

static uint32_t program_dma(void *context)
{
    open_cfw_sched_fixture *state = context;
    state->program_calls++;
    record(7U);
    return state->program_status;
}

void open_cfw_test_mspi_sched_reset(uint32_t token, uint32_t pause_status,
                                    uint32_t program_status,
                                    uint32_t read_value)
{
    uint32_t index;
    fixture.critical_token = token;
    fixture.pause_status = pause_status;
    fixture.program_status = program_status;
    fixture.read_value = read_value;
    fixture.critical_save_calls = 0U;
    fixture.critical_restore_calls = 0U;
    fixture.restored_token = 0U;
    fixture.pause_calls = 0U;
    fixture.read_calls = 0U;
    fixture.read_address = 0U;
    fixture.write_calls = 0U;
    fixture.program_calls = 0U;
    fixture.event_count = 0U;
    for (index = 0U; index < 2U; index++) {
        fixture.write_addresses[index] = 0U;
        fixture.write_values[index] = 0U;
    }
    for (index = 0U; index < OPEN_CFW_SCHED_MAX_EVENTS; index++) {
        fixture.events[index] = 0U;
    }
}

uint32_t open_cfw_test_mspi_sched_run(
    uint32_t module, uint32_t transaction_interrupt, uint32_t active,
    uint32_t pending, uint32_t transaction_count, uint32_t *state_out)
{
    open_cfw_mspi_sched_hiprio_context instance = {
        module, transaction_interrupt, (uint8_t)active, pending
    };
    const open_cfw_mspi_sched_hiprio_ports ports = {
        &fixture, critical_save, critical_restore, command_queue_pause,
        read_reg, write_reg, program_dma
    };
    const uint32_t status = open_cfw_bootloader_mspi_sched_hiprio_4240aa(
        &instance, transaction_count, &ports);
    state_out[0] = instance.transaction_interrupt;
    state_out[1] = instance.high_priority_active;
    state_out[2] = instance.high_priority_entries;
    return status;
}

uint32_t open_cfw_test_mspi_sched_value(uint32_t selector, uint32_t index)
{
    if (selector == 0U) return fixture.critical_save_calls;
    if (selector == 1U) return fixture.critical_restore_calls;
    if (selector == 2U) return fixture.restored_token;
    if (selector == 3U) return fixture.pause_calls;
    if (selector == 4U) return fixture.read_calls;
    if (selector == 5U) return fixture.read_address;
    if (selector == 6U) return fixture.write_calls;
    if (selector == 7U && index < 2U) return fixture.write_addresses[index];
    if (selector == 8U && index < 2U) return fixture.write_values[index];
    if (selector == 9U) return fixture.program_calls;
    if (selector == 10U) return fixture.event_count;
    if (selector == 11U && index < OPEN_CFW_SCHED_MAX_EVENTS)
        return fixture.events[index];
    return 0U;
}
