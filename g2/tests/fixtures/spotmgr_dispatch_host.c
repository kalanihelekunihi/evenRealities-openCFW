/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Native host oracle for the Apollo510 SPOT-manager callback dispatch layer.
 */

#include <stdint.h>

#define OPEN_CFW_TEST_SPOTMGR_DISPATCH_SLOT_COUNT 15U
#define OPEN_CFW_TEST_SPOTMGR_DISPATCH_PRIMARY 1U
#define OPEN_CFW_TEST_SPOTMGR_DISPATCH_SECONDARY 2U

uintptr_t open_cfw_test_spotmgr_dispatch_first[
    OPEN_CFW_TEST_SPOTMGR_DISPATCH_SLOT_COUNT
];
uintptr_t open_cfw_test_spotmgr_dispatch_second[
    OPEN_CFW_TEST_SPOTMGR_DISPATCH_SLOT_COUNT
];
uint32_t open_cfw_test_spotmgr_dispatch_reads[
    OPEN_CFW_TEST_SPOTMGR_DISPATCH_SLOT_COUNT
];
uint32_t open_cfw_test_spotmgr_dispatch_call_count;
uint32_t open_cfw_test_spotmgr_dispatch_last_handler;
uint32_t open_cfw_test_spotmgr_dispatch_argument0;
uint32_t open_cfw_test_spotmgr_dispatch_argument1;
uintptr_t open_cfw_test_spotmgr_dispatch_argument2;
uint32_t open_cfw_test_spotmgr_dispatch_primary_result;
uint32_t open_cfw_test_spotmgr_dispatch_secondary_result;

static uint32_t open_cfw_test_spotmgr_dispatch_noarg_primary(void)
{
    ++open_cfw_test_spotmgr_dispatch_call_count;
    open_cfw_test_spotmgr_dispatch_last_handler =
        OPEN_CFW_TEST_SPOTMGR_DISPATCH_PRIMARY;
    return open_cfw_test_spotmgr_dispatch_primary_result;
}

static uint32_t open_cfw_test_spotmgr_dispatch_noarg_secondary(void)
{
    ++open_cfw_test_spotmgr_dispatch_call_count;
    open_cfw_test_spotmgr_dispatch_last_handler =
        OPEN_CFW_TEST_SPOTMGR_DISPATCH_SECONDARY;
    return open_cfw_test_spotmgr_dispatch_secondary_result;
}

static uint32_t open_cfw_test_spotmgr_dispatch_power_primary(
    uint32_t stimulus,
    uint32_t enabled,
    void *arguments
)
{
    ++open_cfw_test_spotmgr_dispatch_call_count;
    open_cfw_test_spotmgr_dispatch_last_handler =
        OPEN_CFW_TEST_SPOTMGR_DISPATCH_PRIMARY;
    open_cfw_test_spotmgr_dispatch_argument0 = stimulus;
    open_cfw_test_spotmgr_dispatch_argument1 = enabled;
    open_cfw_test_spotmgr_dispatch_argument2 = (uintptr_t)arguments;
    return open_cfw_test_spotmgr_dispatch_primary_result;
}

static uint32_t open_cfw_test_spotmgr_dispatch_power_secondary(
    uint32_t stimulus,
    uint32_t enabled,
    void *arguments
)
{
    ++open_cfw_test_spotmgr_dispatch_call_count;
    open_cfw_test_spotmgr_dispatch_last_handler =
        OPEN_CFW_TEST_SPOTMGR_DISPATCH_SECONDARY;
    open_cfw_test_spotmgr_dispatch_argument0 = stimulus;
    open_cfw_test_spotmgr_dispatch_argument1 = enabled;
    open_cfw_test_spotmgr_dispatch_argument2 = (uintptr_t)arguments;
    return open_cfw_test_spotmgr_dispatch_secondary_result;
}

static uint32_t open_cfw_test_spotmgr_dispatch_ton_primary(
    uint32_t enabled,
    uint32_t state
)
{
    ++open_cfw_test_spotmgr_dispatch_call_count;
    open_cfw_test_spotmgr_dispatch_last_handler =
        OPEN_CFW_TEST_SPOTMGR_DISPATCH_PRIMARY;
    open_cfw_test_spotmgr_dispatch_argument0 = enabled;
    open_cfw_test_spotmgr_dispatch_argument1 = state;
    return open_cfw_test_spotmgr_dispatch_primary_result;
}

static uint32_t open_cfw_test_spotmgr_dispatch_ton_secondary(
    uint32_t enabled,
    uint32_t state
)
{
    ++open_cfw_test_spotmgr_dispatch_call_count;
    open_cfw_test_spotmgr_dispatch_last_handler =
        OPEN_CFW_TEST_SPOTMGR_DISPATCH_SECONDARY;
    open_cfw_test_spotmgr_dispatch_argument0 = enabled;
    open_cfw_test_spotmgr_dispatch_argument1 = state;
    return open_cfw_test_spotmgr_dispatch_secondary_result;
}

static void open_cfw_test_spotmgr_dispatch_timer_primary(void)
{
    ++open_cfw_test_spotmgr_dispatch_call_count;
    open_cfw_test_spotmgr_dispatch_last_handler =
        OPEN_CFW_TEST_SPOTMGR_DISPATCH_PRIMARY;
}

static void open_cfw_test_spotmgr_dispatch_timer_secondary(void)
{
    ++open_cfw_test_spotmgr_dispatch_call_count;
    open_cfw_test_spotmgr_dispatch_last_handler =
        OPEN_CFW_TEST_SPOTMGR_DISPATCH_SECONDARY;
}

static uintptr_t
open_cfw_test_spotmgr_dispatch_read_handler(uint32_t offset)
{
    uint32_t index = offset / 4U;
    uintptr_t handler;

    if (
        index >= OPEN_CFW_TEST_SPOTMGR_DISPATCH_SLOT_COUNT
        || (offset & 3U) != 0U
    ) {
        return (uintptr_t)0U;
    }

    if (open_cfw_test_spotmgr_dispatch_reads[index] == 0U) {
        handler = open_cfw_test_spotmgr_dispatch_first[index];
    }
    else {
        handler = open_cfw_test_spotmgr_dispatch_second[index];
    }
    ++open_cfw_test_spotmgr_dispatch_reads[index];
    return handler;
}

#define OPEN_CFW_SPOTMGR_DISPATCH_READ_HANDLER(offset) \
    open_cfw_test_spotmgr_dispatch_read_handler(offset)

#include "../../components/apollo_main/core_overlay/spotmgr_dispatch.c"

void open_cfw_test_spotmgr_dispatch_reset(void)
{
    uint32_t index;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_SPOTMGR_DISPATCH_SLOT_COUNT;
        ++index
    ) {
        open_cfw_test_spotmgr_dispatch_first[index] = (uintptr_t)0U;
        open_cfw_test_spotmgr_dispatch_second[index] = (uintptr_t)0U;
        open_cfw_test_spotmgr_dispatch_reads[index] = 0U;
    }
    open_cfw_test_spotmgr_dispatch_call_count = 0U;
    open_cfw_test_spotmgr_dispatch_last_handler = 0U;
    open_cfw_test_spotmgr_dispatch_argument0 = 0U;
    open_cfw_test_spotmgr_dispatch_argument1 = 0U;
    open_cfw_test_spotmgr_dispatch_argument2 = (uintptr_t)0U;
    open_cfw_test_spotmgr_dispatch_primary_result = 0x13579BDFU;
    open_cfw_test_spotmgr_dispatch_secondary_result = 0x2468ACE0U;
}

void open_cfw_test_spotmgr_dispatch_configure(
    uint32_t offset,
    uint32_t mode
)
{
    uint32_t index = offset / 4U;
    uintptr_t primary;
    uintptr_t secondary;

    if (
        index >= OPEN_CFW_TEST_SPOTMGR_DISPATCH_SLOT_COUNT
        || (offset & 3U) != 0U
    ) {
        return;
    }

    if (offset == 0x04U) {
        primary = (uintptr_t)open_cfw_test_spotmgr_dispatch_power_primary;
        secondary =
            (uintptr_t)open_cfw_test_spotmgr_dispatch_power_secondary;
    }
    else if (offset == 0x24U) {
        primary = (uintptr_t)open_cfw_test_spotmgr_dispatch_ton_primary;
        secondary = (uintptr_t)open_cfw_test_spotmgr_dispatch_ton_secondary;
    }
    else if (offset == 0x2CU) {
        primary = (uintptr_t)open_cfw_test_spotmgr_dispatch_timer_primary;
        secondary =
            (uintptr_t)open_cfw_test_spotmgr_dispatch_timer_secondary;
    }
    else {
        primary = (uintptr_t)open_cfw_test_spotmgr_dispatch_noarg_primary;
        secondary =
            (uintptr_t)open_cfw_test_spotmgr_dispatch_noarg_secondary;
    }

    if (mode == 0U) {
        primary = (uintptr_t)0U;
        secondary = (uintptr_t)0U;
    }
    else if (mode == 1U) {
        secondary = primary;
    }
    open_cfw_test_spotmgr_dispatch_first[index] = primary;
    open_cfw_test_spotmgr_dispatch_second[index] = secondary;
}
