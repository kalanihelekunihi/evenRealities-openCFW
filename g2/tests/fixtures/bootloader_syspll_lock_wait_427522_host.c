/* SPDX-License-Identifier: MIT */
#include <stdint.h>

static uint32_t host_pllctl0_first;
static uint32_t host_pllctl0_second;
static uint32_t host_plldiv1;
static uint32_t host_status_return;
static uint32_t host_pllctl0_reads;
static uint32_t host_plldiv1_reads;
static uint32_t host_status_calls;
static uint32_t host_order;
static uint32_t host_timeout;
static uint32_t host_address;
static uint32_t host_mask;
static uint32_t host_expected;
static uint32_t host_equality;

uint32_t open_cfw_host_syspll_lock_wait_pllctl0_read(void)
{
    uint32_t value = host_pllctl0_reads == 0U ?
        host_pllctl0_first : host_pllctl0_second;
    host_pllctl0_reads += 1U;
    host_order = host_order * 10U + 1U;
    return value;
}

uint32_t open_cfw_host_syspll_lock_wait_plldiv1_read(void)
{
    host_plldiv1_reads += 1U;
    host_order = host_order * 10U + 2U;
    return host_plldiv1;
}

uint32_t open_cfw_host_syspll_lock_wait_status_check(
    uint32_t timeout_us, uint32_t address, uint32_t mask,
    uint32_t expected, uint32_t equality)
{
    host_status_calls += 1U;
    host_order = host_order * 10U + 3U;
    host_timeout = timeout_us;
    host_address = address;
    host_mask = mask;
    host_expected = expected;
    host_equality = equality;
    return host_status_return;
}

#define OPEN_CFW_SYSPLL_LOCK_WAIT_HOST_TEST 1
#include "../../components/bootloader/core_overlay/runtime_syspll_lock_wait_427522.c"

static open_cfw_syspll_lock_wait_state host_state;

void open_cfw_host_syspll_lock_wait_reset(
    uint32_t prefix, uint32_t module, uint32_t pllctl0_first,
    uint32_t plldiv1, uint32_t pllctl0_second, uint32_t status_return)
{
    host_state.prefix = prefix;
    host_state.module = module;
    host_pllctl0_first = pllctl0_first;
    host_pllctl0_second = pllctl0_second;
    host_plldiv1 = plldiv1;
    host_status_return = status_return;
    host_pllctl0_reads = 0U;
    host_plldiv1_reads = 0U;
    host_status_calls = 0U;
    host_order = 0U;
    host_timeout = 0U;
    host_address = 0U;
    host_mask = 0U;
    host_expected = 0U;
    host_equality = 0U;
}

uint32_t open_cfw_host_syspll_lock_wait_call(void)
{
    return open_cfw_bootloader_row6_lock_wait_427522(&host_state);
}

#define OPEN_CFW_HOST_GETTER(name, value) \
    uint32_t name(void) { return (value); }
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_lock_wait_pllctl0_reads,
                     host_pllctl0_reads)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_lock_wait_plldiv1_reads,
                     host_plldiv1_reads)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_lock_wait_status_calls,
                     host_status_calls)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_lock_wait_order, host_order)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_lock_wait_timeout, host_timeout)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_lock_wait_address, host_address)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_lock_wait_mask, host_mask)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_lock_wait_expected, host_expected)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_lock_wait_equality, host_equality)
