#include <stdint.h>

uintptr_t open_cfw_mode0_host_controller;
uint8_t open_cfw_mode0_host_table_mode;
uint8_t open_cfw_mode0_host_active;
uint32_t open_cfw_mode0_host_runtime_value;
uint32_t *open_cfw_mode0_host_state_pointer;

uint32_t open_cfw_mode0_fixture_bitmap[2];
uint8_t open_cfw_mode0_fixture_query_state;
uint32_t open_cfw_mode0_fixture_query_calls;
uint32_t open_cfw_mode0_fixture_update_calls;
uint32_t open_cfw_mode0_fixture_update_bit;
uint32_t open_cfw_mode0_fixture_control_calls;
uint32_t open_cfw_mode0_fixture_control_request;
uint32_t open_cfw_mode0_fixture_control_argument;
uint32_t open_cfw_mode0_fixture_cleanup_calls;
uint32_t open_cfw_mode0_fixture_cleanup_value;
uint32_t open_cfw_mode0_fixture_restore_calls;

uint32_t open_cfw_mode0_host_bitmap_test(uint32_t row, uint32_t bit)
{
    if (row != 2U || bit >= 64U) return 0U;
    return (open_cfw_mode0_fixture_bitmap[bit >> 5] >> (bit & 31U)) & 1U;
}

uint32_t open_cfw_mode0_host_bitmap_update(uint32_t row, uint32_t bit, uint32_t enabled)
{
    ++open_cfw_mode0_fixture_update_calls;
    open_cfw_mode0_fixture_update_bit = bit;
    if (row == 2U && bit < 64U && enabled != 0U)
        open_cfw_mode0_fixture_bitmap[bit >> 5] |= 1U << (bit & 31U);
    return 0U;
}

uint32_t open_cfw_mode0_host_critical_save(void) { return 0x77U; }
void open_cfw_mode0_host_critical_restore(uint32_t mask)
{
    if (mask == 0x77U) ++open_cfw_mode0_fixture_restore_calls;
}

void open_cfw_mode0_host_cleanup(uint32_t *remaining)
{
    ++open_cfw_mode0_fixture_cleanup_calls;
    open_cfw_mode0_fixture_cleanup_value = *remaining;
    open_cfw_mode0_host_active = 0U;
    open_cfw_mode0_host_state_pointer = 0;
}

void open_cfw_mode0_host_state_query(uint8_t *state)
{
    ++open_cfw_mode0_fixture_query_calls;
    *state = open_cfw_mode0_fixture_query_state;
}

uint32_t open_cfw_mode0_host_control(uint32_t request, uint8_t *argument)
{
    ++open_cfw_mode0_fixture_control_calls;
    open_cfw_mode0_fixture_control_request = request;
    open_cfw_mode0_fixture_control_argument = argument == 0 ? 0U : *argument;
    return 0U;
}

#include "../../components/bootloader/core_overlay/runtime_mode0_enable_421bd2.c"

void open_cfw_mode0_fixture_reset(void)
{
    open_cfw_mode0_host_controller = 0U;
    open_cfw_mode0_host_table_mode = 0U;
    open_cfw_mode0_host_active = 0U;
    open_cfw_mode0_host_runtime_value = 0U;
    open_cfw_mode0_host_state_pointer = 0;
    open_cfw_mode0_fixture_bitmap[0] = 0U;
    open_cfw_mode0_fixture_bitmap[1] = 0U;
    open_cfw_mode0_fixture_query_state = 0U;
    open_cfw_mode0_fixture_query_calls = 0U;
    open_cfw_mode0_fixture_update_calls = 0U;
    open_cfw_mode0_fixture_update_bit = 0U;
    open_cfw_mode0_fixture_control_calls = 0U;
    open_cfw_mode0_fixture_control_request = 0U;
    open_cfw_mode0_fixture_control_argument = 0U;
    open_cfw_mode0_fixture_cleanup_calls = 0U;
    open_cfw_mode0_fixture_cleanup_value = 0U;
    open_cfw_mode0_fixture_restore_calls = 0U;
}
