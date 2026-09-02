/* SPDX-License-Identifier: MIT */
#include <stdint.h>

static uint32_t host_token;
static uint32_t host_save_calls;
static uint32_t host_restore_calls;
static uint32_t host_restored_token;
static uint32_t host_order;

uint32_t open_cfw_cmdq_host_critical_save(void)
{
    host_save_calls += 1U;
    host_order = host_order * 10U + 1U;
    return host_token;
}

void open_cfw_cmdq_host_critical_restore(uint32_t token)
{
    host_restore_calls += 1U;
    host_restored_token = token;
    host_order = host_order * 10U + 2U;
}

#define OPEN_CFW_CMDQ_HOST_TEST 1
#include "../../components/bootloader/core_overlay/runtime_cmdq_update_indices_427754.c"

static open_cfw_cmdq_state host_queue;
static open_cfw_cmdq_registers host_registers;
static uint32_t host_queue_address;
static uint32_t host_current_index;

void open_cfw_cmdq_host_reset(uint32_t token, uint32_t end_index,
                              uint32_t hardware_index,
                              uint32_t queue_address)
{
    host_token = token;
    host_save_calls = 0U;
    host_restore_calls = 0U;
    host_restored_token = 0U;
    host_order = 0U;
    host_queue_address = queue_address;
    host_current_index = hardware_index;
    host_registers.queue_address = &host_queue_address;
    host_registers.current_index = &host_current_index;
    host_queue.head = 0xAAAAAAAAU;
    host_queue.current_index = 0xBBBBBBBBU;
    host_queue.end_index = end_index;
    host_queue.registers = &host_registers;
}

void open_cfw_cmdq_host_run(void)
{
    open_cfw_bootloader_cmdq_update_indices_427754(&host_queue);
}

#define OPEN_CFW_CMDQ_HOST_GETTER(name, value) \
    uint32_t name(void) { return (value); }
OPEN_CFW_CMDQ_HOST_GETTER(open_cfw_cmdq_host_head, host_queue.head)
OPEN_CFW_CMDQ_HOST_GETTER(open_cfw_cmdq_host_current, host_queue.current_index)
OPEN_CFW_CMDQ_HOST_GETTER(open_cfw_cmdq_host_save_calls, host_save_calls)
OPEN_CFW_CMDQ_HOST_GETTER(open_cfw_cmdq_host_restore_calls, host_restore_calls)
OPEN_CFW_CMDQ_HOST_GETTER(open_cfw_cmdq_host_restored_token,
                         host_restored_token)
OPEN_CFW_CMDQ_HOST_GETTER(open_cfw_cmdq_host_order, host_order)
