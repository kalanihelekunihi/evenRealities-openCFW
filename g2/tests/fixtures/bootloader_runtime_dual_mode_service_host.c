/* SPDX-License-Identifier: MIT */

#include <stdint.h>

uint32_t open_cfw_dual_host_controller0;
uint32_t open_cfw_dual_host_controller1;
uintptr_t open_cfw_dual_host_current;
uint32_t open_cfw_dual_host_configuration[3];
uint8_t open_cfw_dual_host_ready;

uint32_t open_cfw_dual_fixture_query_status;
uint32_t open_cfw_dual_fixture_query_value;
uint32_t open_cfw_dual_fixture_query_calls;
uint32_t open_cfw_dual_fixture_query_controller;
uintptr_t open_cfw_dual_fixture_query_instance;
uint32_t open_cfw_dual_fixture_query_option;
uint32_t open_cfw_dual_fixture_bitmap_values[2];
uint32_t open_cfw_dual_fixture_bitmap_calls;
uint32_t open_cfw_dual_fixture_bitmap_selector;
uint32_t open_cfw_dual_fixture_saved_masks[2];
uint32_t open_cfw_dual_fixture_save_calls;
uint32_t open_cfw_dual_fixture_restored_masks[2];
uint32_t open_cfw_dual_fixture_restore_calls;
uint32_t open_cfw_dual_fixture_copy_calls;
uint32_t open_cfw_dual_fixture_copy_size;
uint32_t open_cfw_dual_fixture_mode0_enable_calls;
uint32_t open_cfw_dual_fixture_mode1_enable_calls;
uint32_t open_cfw_dual_fixture_mode0_disable_calls;
uint32_t open_cfw_dual_fixture_mode1_disable_calls;
uint32_t open_cfw_dual_fixture_null_commit_calls;
uint32_t open_cfw_dual_fixture_commit_calls;
uint32_t open_cfw_dual_fixture_null_commit_status;
uint32_t open_cfw_dual_fixture_commit_status;
uint32_t open_cfw_dual_fixture_last_argument;

uint32_t open_cfw_dual_host_query(
    uint32_t controller, uintptr_t instance, uint32_t option, uint32_t *output)
{
    open_cfw_dual_fixture_query_calls += 1U;
    open_cfw_dual_fixture_query_controller = controller;
    open_cfw_dual_fixture_query_instance = instance;
    open_cfw_dual_fixture_query_option = option;
    *output = open_cfw_dual_fixture_query_value;
    return open_cfw_dual_fixture_query_status;
}

uint32_t open_cfw_dual_host_critical_save(void)
{
    uint32_t index = open_cfw_dual_fixture_save_calls++;
    return open_cfw_dual_fixture_saved_masks[index < 2U ? index : 1U];
}

void open_cfw_dual_host_critical_restore(uint32_t mask)
{
    uint32_t index = open_cfw_dual_fixture_restore_calls++;
    if (index < 2U) {
        open_cfw_dual_fixture_restored_masks[index] = mask;
    }
}

uint32_t open_cfw_dual_host_bitmap_count(uint32_t selector)
{
    uint32_t index = open_cfw_dual_fixture_bitmap_calls++;
    open_cfw_dual_fixture_bitmap_selector = selector;
    return open_cfw_dual_fixture_bitmap_values[index < 2U ? index : 1U];
}

void open_cfw_dual_host_copy(void *destination, const void *source, uint32_t size)
{
    uint8_t *out = (uint8_t *)destination;
    const uint8_t *in = (const uint8_t *)source;
    uint32_t index;
    open_cfw_dual_fixture_copy_calls += 1U;
    open_cfw_dual_fixture_copy_size = size;
    for (index = 0U; index < size; ++index) {
        out[index] = in[index];
    }
}

uint32_t open_cfw_dual_host_mode0_enable(uint32_t argument)
{
    open_cfw_dual_fixture_mode0_enable_calls += 1U;
    open_cfw_dual_fixture_last_argument = argument;
    return 0U;
}

uint32_t open_cfw_dual_host_mode1_enable(uint32_t argument)
{
    open_cfw_dual_fixture_mode1_enable_calls += 1U;
    open_cfw_dual_fixture_last_argument = argument;
    return 0U;
}

uint32_t open_cfw_dual_host_null_commit(void)
{
    open_cfw_dual_fixture_null_commit_calls += 1U;
    return open_cfw_dual_fixture_null_commit_status;
}

uint32_t open_cfw_dual_host_commit(uint8_t *configuration)
{
    (void)configuration;
    open_cfw_dual_fixture_commit_calls += 1U;
    return open_cfw_dual_fixture_commit_status;
}

uint32_t open_cfw_dual_host_mode1_disable(uint32_t argument)
{
    open_cfw_dual_fixture_mode1_disable_calls += 1U;
    open_cfw_dual_fixture_last_argument = argument;
    return 0U;
}

uint32_t open_cfw_dual_host_mode0_disable(uint32_t argument)
{
    open_cfw_dual_fixture_mode0_disable_calls += 1U;
    open_cfw_dual_fixture_last_argument = argument;
    return 0U;
}

#include "../../components/bootloader/core_overlay/runtime_dual_mode_service_4217d2.c"

void open_cfw_dual_fixture_reset(void)
{
    open_cfw_dual_host_controller0 = 0U;
    open_cfw_dual_host_controller1 = 0U;
    open_cfw_dual_host_current = 0U;
    open_cfw_dual_host_configuration[0] = 0U;
    open_cfw_dual_host_configuration[1] = 0U;
    open_cfw_dual_host_configuration[2] = 0U;
    open_cfw_dual_host_ready = 0U;
    open_cfw_dual_fixture_query_status = 0U;
    open_cfw_dual_fixture_query_value = 0xAABBCCDDU;
    open_cfw_dual_fixture_query_calls = 0U;
    open_cfw_dual_fixture_query_controller = 0U;
    open_cfw_dual_fixture_query_instance = 0U;
    open_cfw_dual_fixture_query_option = 0U;
    open_cfw_dual_fixture_bitmap_values[0] = 0U;
    open_cfw_dual_fixture_bitmap_values[1] = 0U;
    open_cfw_dual_fixture_bitmap_calls = 0U;
    open_cfw_dual_fixture_bitmap_selector = 0U;
    open_cfw_dual_fixture_saved_masks[0] = 0x11U;
    open_cfw_dual_fixture_saved_masks[1] = 0x22U;
    open_cfw_dual_fixture_save_calls = 0U;
    open_cfw_dual_fixture_restored_masks[0] = 0U;
    open_cfw_dual_fixture_restored_masks[1] = 0U;
    open_cfw_dual_fixture_restore_calls = 0U;
    open_cfw_dual_fixture_copy_calls = 0U;
    open_cfw_dual_fixture_copy_size = 0U;
    open_cfw_dual_fixture_mode0_enable_calls = 0U;
    open_cfw_dual_fixture_mode1_enable_calls = 0U;
    open_cfw_dual_fixture_mode0_disable_calls = 0U;
    open_cfw_dual_fixture_mode1_disable_calls = 0U;
    open_cfw_dual_fixture_null_commit_calls = 0U;
    open_cfw_dual_fixture_commit_calls = 0U;
    open_cfw_dual_fixture_null_commit_status = 0U;
    open_cfw_dual_fixture_commit_status = 0U;
    open_cfw_dual_fixture_last_argument = 0U;
}
