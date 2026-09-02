/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>

#define OPEN_CFW_CMDQ_SERVICES_HOST_TEST 1
#include "../../components/bootloader/core_overlay/runtime_cmdq_services_427794.c"

enum {
    HOST_ENTRY_COUNT = 512,
    HOST_BUFFER_BASE = 0x10000000U,
    HOST_REGISTER_BASE = 0x50000000U,
    HOST_REGISTER_STRIDE = 0x100U
};

open_cfw_cmdq_state open_cfw_cmdq_host_states[OPEN_CFW_CMDQ_INTERFACE_COUNT];
open_cfw_cmdq_registers
    open_cfw_cmdq_host_registers[OPEN_CFW_CMDQ_INTERFACE_COUNT];

static open_cfw_cmdq_entry host_entries[HOST_ENTRY_COUNT];
static open_cfw_cmdq_u32 host_register_values[OPEN_CFW_CMDQ_INTERFACE_COUNT][7];
static open_cfw_cmdq_u32 host_dmb_calls;
static open_cfw_cmdq_u32 host_update_calls;

open_cfw_cmdq_entry *
open_cfw_cmdq_host_resolve(open_cfw_cmdq_u32 address)
{
    open_cfw_cmdq_u32 offset;
    if (address < HOST_BUFFER_BASE) {
        return (open_cfw_cmdq_entry *)0;
    }
    offset = address - HOST_BUFFER_BASE;
    if ((offset & 7U) != 0U || offset / 8U >= HOST_ENTRY_COUNT) {
        return (open_cfw_cmdq_entry *)0;
    }
    return &host_entries[offset / 8U];
}

open_cfw_cmdq_u32
open_cfw_cmdq_host_register_address(
    const volatile open_cfw_cmdq_u32 *register_pointer)
{
    open_cfw_cmdq_u32 interface_index;
    open_cfw_cmdq_u32 register_index;
    for (interface_index = 0U;
         interface_index < OPEN_CFW_CMDQ_INTERFACE_COUNT;
         ++interface_index) {
        for (register_index = 0U; register_index < 7U; ++register_index) {
            if (register_pointer ==
                &host_register_values[interface_index][register_index]) {
                return HOST_REGISTER_BASE +
                    interface_index * HOST_REGISTER_STRIDE +
                    register_index * 4U;
            }
        }
    }
    return 0U;
}

void open_cfw_cmdq_host_dmb(void)
{
    host_dmb_calls += 1U;
}

void
open_cfw_bootloader_cmdq_update_indices_427754(open_cfw_cmdq_state *queue)
{
    open_cfw_cmdq_u32 hardware_current =
        *queue->registers->current_index & 0xFFU;
    host_update_calls += 1U;
    queue->current_index = (queue->end_index & ~0xFFU) | hardware_current;
    if ((open_cfw_cmdq_s32)(queue->end_index - queue->current_index) < 0) {
        queue->current_index -= 0x100U;
    }
    queue->head = *queue->registers->queue_address;
}

void open_cfw_cmdq_services_host_reset(void)
{
    open_cfw_cmdq_u32 interface_index;
    open_cfw_cmdq_u32 register_index;
    open_cfw_cmdq_u32 entry_index;

    for (interface_index = 0U;
         interface_index < OPEN_CFW_CMDQ_INTERFACE_COUNT;
         ++interface_index) {
        open_cfw_cmdq_state *state =
            &open_cfw_cmdq_host_states[interface_index];
        state->prefix = 0U;
        state->buffer_start = 0U;
        state->buffer_end = 0U;
        state->head = 0U;
        state->tail = 0U;
        state->next_tail = 0U;
        state->size = 0U;
        state->current_index = 0U;
        state->end_index = 0U;
        state->registers = &open_cfw_cmdq_host_registers[interface_index];
        state->raw_sequence_start = 0U;
        for (register_index = 0U; register_index < 7U; ++register_index) {
            host_register_values[interface_index][register_index] = 0U;
        }
        open_cfw_cmdq_host_registers[interface_index].configuration =
            &host_register_values[interface_index][0];
        open_cfw_cmdq_host_registers[interface_index].queue_address =
            &host_register_values[interface_index][1];
        open_cfw_cmdq_host_registers[interface_index].current_index =
            &host_register_values[interface_index][2];
        open_cfw_cmdq_host_registers[interface_index].end_index =
            &host_register_values[interface_index][3];
        open_cfw_cmdq_host_registers[interface_index].pause =
            &host_register_values[interface_index][4];
        open_cfw_cmdq_host_registers[interface_index].pause_index_mask = 0x40U;
        open_cfw_cmdq_host_registers[interface_index].status =
            &host_register_values[interface_index][6];
        open_cfw_cmdq_host_registers[interface_index].tip_mask = 0x1U;
        open_cfw_cmdq_host_registers[interface_index].error_mask = 0x4U;
        open_cfw_cmdq_host_registers[interface_index].paused_mask = 0x2U;
    }
    for (entry_index = 0U; entry_index < HOST_ENTRY_COUNT; ++entry_index) {
        host_entries[entry_index].address = 0U;
        host_entries[entry_index].value = 0U;
    }
    host_dmb_calls = 0U;
    host_update_calls = 0U;
}

void *open_cfw_cmdq_services_host_state(open_cfw_cmdq_u32 interface_index)
{
    return &open_cfw_cmdq_host_states[interface_index];
}

void *open_cfw_cmdq_services_host_entry(open_cfw_cmdq_u32 entry_index)
{
    return &host_entries[entry_index];
}

void
open_cfw_cmdq_services_host_set_register(open_cfw_cmdq_u32 interface_index,
                                         open_cfw_cmdq_u32 register_index,
                                         open_cfw_cmdq_u32 value)
{
    host_register_values[interface_index][register_index] = value;
}

open_cfw_cmdq_u32
open_cfw_cmdq_services_host_get_register(open_cfw_cmdq_u32 interface_index,
                                         open_cfw_cmdq_u32 register_index)
{
    return host_register_values[interface_index][register_index];
}

open_cfw_cmdq_u32 open_cfw_cmdq_services_host_register_token(
    open_cfw_cmdq_u32 interface_index, open_cfw_cmdq_u32 register_index)
{
    return HOST_REGISTER_BASE + interface_index * HOST_REGISTER_STRIDE +
        register_index * 4U;
}

open_cfw_cmdq_u32 open_cfw_cmdq_services_host_buffer_base(void)
{
    return HOST_BUFFER_BASE;
}

open_cfw_cmdq_u32 open_cfw_cmdq_services_host_dmb_calls(void)
{
    return host_dmb_calls;
}

open_cfw_cmdq_u32 open_cfw_cmdq_services_host_update_calls(void)
{
    return host_update_calls;
}
