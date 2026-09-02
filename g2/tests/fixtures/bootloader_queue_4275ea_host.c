/* SPDX-License-Identifier: MIT */
#include <stdint.h>

static uint32_t host_token;
static uint32_t host_save_calls;
static uint32_t host_restore_calls;
static uint32_t host_restored_token;
static uint32_t host_order;

uint32_t open_cfw_queue_host_critical_save(void)
{
    host_save_calls += 1U;
    host_order = host_order * 10U + 1U;
    return host_token;
}

void open_cfw_queue_host_critical_restore(uint32_t token)
{
    host_restore_calls += 1U;
    host_restored_token = token;
    host_order = host_order * 10U + 2U;
}

#define OPEN_CFW_QUEUE_HOST_TEST 1
#include "../../components/bootloader/core_overlay/runtime_queue_4275ea.c"

void open_cfw_queue_host_reset(uint32_t token)
{
    host_token = token;
    host_save_calls = 0U;
    host_restore_calls = 0U;
    host_restored_token = 0U;
    host_order = 0U;
}

#define OPEN_CFW_QUEUE_HOST_GETTER(name, value) \
    uint32_t name(void) { return (value); }
OPEN_CFW_QUEUE_HOST_GETTER(open_cfw_queue_host_save_calls, host_save_calls)
OPEN_CFW_QUEUE_HOST_GETTER(open_cfw_queue_host_restore_calls,
                           host_restore_calls)
OPEN_CFW_QUEUE_HOST_GETTER(open_cfw_queue_host_restored_token,
                           host_restored_token)
OPEN_CFW_QUEUE_HOST_GETTER(open_cfw_queue_host_order, host_order)
