/* SPDX-License-Identifier: MIT */

#include <stdint.h>

uint32_t open_cfw_mode_host_controller;
uintptr_t open_cfw_mode_host_current;
uint32_t open_cfw_mode_host_fallback[3];
uint8_t open_cfw_mode_host_aux_flag;
uint32_t open_cfw_mode_host_aux_word;
uint8_t open_cfw_mode_host_ready;

uint32_t open_cfw_mode_fixture_query_status;
uint32_t open_cfw_mode_fixture_query_value;
uint32_t open_cfw_mode_fixture_bitmap_count;
uint32_t open_cfw_mode_fixture_disable_status;
uint32_t open_cfw_mode_fixture_apply_status[2];
uint32_t open_cfw_mode_fixture_apply_values[2];
uint32_t open_cfw_mode_fixture_apply_calls;
uint32_t open_cfw_mode_fixture_disable_calls;
uint32_t open_cfw_mode_fixture_query_calls;
uint32_t open_cfw_mode_fixture_copy_calls;
uint32_t open_cfw_mode_fixture_saved_mask;
uint32_t open_cfw_mode_fixture_restored_mask;
uint32_t open_cfw_mode_fixture_bitmap_selector;
uint32_t open_cfw_mode_fixture_copy_size;
uintptr_t open_cfw_mode_fixture_query_instance;
uint32_t open_cfw_mode_fixture_query_controller;

uint32_t open_cfw_mode_host_query(
    uint32_t controller, uintptr_t instance, uint32_t *value)
{
    open_cfw_mode_fixture_query_calls += 1U;
    open_cfw_mode_fixture_query_controller = controller;
    open_cfw_mode_fixture_query_instance = instance;
    *value = open_cfw_mode_fixture_query_value;
    return open_cfw_mode_fixture_query_status;
}

uint32_t open_cfw_mode_host_critical_save(void)
{
    return open_cfw_mode_fixture_saved_mask;
}

void open_cfw_mode_host_critical_restore(uint32_t mask)
{
    open_cfw_mode_fixture_restored_mask = mask;
}

uint32_t open_cfw_mode_host_bitmap_count(uint32_t selector)
{
    open_cfw_mode_fixture_bitmap_selector = selector;
    return open_cfw_mode_fixture_bitmap_count;
}

uint32_t open_cfw_mode_host_disable(void)
{
    open_cfw_mode_fixture_disable_calls += 1U;
    return open_cfw_mode_fixture_disable_status;
}

uint32_t open_cfw_mode_host_apply(uint32_t value)
{
    uint32_t index = open_cfw_mode_fixture_apply_calls;
    if (index < 2U) {
        open_cfw_mode_fixture_apply_values[index] = value;
    }
    open_cfw_mode_fixture_apply_calls += 1U;
    return open_cfw_mode_fixture_apply_status[index < 2U ? index : 1U];
}

void open_cfw_mode_host_copy(void *destination, const void *source, uint32_t size)
{
    uint8_t *out = (uint8_t *)destination;
    const uint8_t *in = (const uint8_t *)source;
    uint32_t index;
    open_cfw_mode_fixture_copy_calls += 1U;
    open_cfw_mode_fixture_copy_size = size;
    for (index = 0U; index < size; ++index) {
        out[index] = in[index];
    }
}

#include "../../components/bootloader/core_overlay/runtime_mode_service_4216d4.c"

void open_cfw_mode_fixture_reset(void)
{
    open_cfw_mode_host_controller = 0U;
    open_cfw_mode_host_current = 0U;
    open_cfw_mode_host_fallback[0] = 0x11111111U;
    open_cfw_mode_host_fallback[1] = 0x22222222U;
    open_cfw_mode_host_fallback[2] = 0x33333333U;
    open_cfw_mode_host_aux_flag = 1U;
    open_cfw_mode_host_aux_word = 0xFFFFFFFFU;
    open_cfw_mode_host_ready = 0U;
    open_cfw_mode_fixture_query_status = 0U;
    open_cfw_mode_fixture_query_value = 0U;
    open_cfw_mode_fixture_bitmap_count = 0U;
    open_cfw_mode_fixture_disable_status = 0U;
    open_cfw_mode_fixture_apply_status[0] = 0U;
    open_cfw_mode_fixture_apply_status[1] = 0U;
    open_cfw_mode_fixture_apply_values[0] = 0U;
    open_cfw_mode_fixture_apply_values[1] = 0U;
    open_cfw_mode_fixture_apply_calls = 0U;
    open_cfw_mode_fixture_disable_calls = 0U;
    open_cfw_mode_fixture_query_calls = 0U;
    open_cfw_mode_fixture_copy_calls = 0U;
    open_cfw_mode_fixture_saved_mask = 0xA5U;
    open_cfw_mode_fixture_restored_mask = 0U;
    open_cfw_mode_fixture_bitmap_selector = 0U;
    open_cfw_mode_fixture_copy_size = 0U;
    open_cfw_mode_fixture_query_instance = 0U;
    open_cfw_mode_fixture_query_controller = 0U;
}
