#include <stdint.h>

uintptr_t open_cfw_mode1_host_controller;
uint32_t open_cfw_mode1_host_enable_word;
uint32_t open_cfw_mode1_host_disable_word;
uint8_t open_cfw_mode1_host_active;
uint32_t open_cfw_mode1_host_state;

uint32_t open_cfw_mode1_fixture_bitmap[2];
uint32_t open_cfw_mode1_fixture_save_calls;
uint32_t open_cfw_mode1_fixture_restore_calls;
uint32_t open_cfw_mode1_fixture_control_calls;
uint32_t open_cfw_mode1_fixture_control_request;
uint32_t open_cfw_mode1_fixture_control_value;
uint32_t open_cfw_mode1_fixture_update_calls;
uint32_t open_cfw_mode1_fixture_update_bit;
uint32_t open_cfw_mode1_fixture_update_enabled;
uint32_t open_cfw_mode1_fixture_poll_calls;
uint32_t *open_cfw_mode1_fixture_poll_remaining;

uint32_t open_cfw_mode1_host_bitmap_test(uint32_t row, uint32_t bit)
{
    if (row != 3U || bit >= 64U) return 0U;
    return (open_cfw_mode1_fixture_bitmap[bit >> 5] >> (bit & 31U)) & 1U;
}

uint32_t open_cfw_mode1_host_bitmap_update(uint32_t row, uint32_t bit, uint32_t enabled)
{
    uint32_t mask;
    ++open_cfw_mode1_fixture_update_calls;
    open_cfw_mode1_fixture_update_bit = bit;
    open_cfw_mode1_fixture_update_enabled = enabled;
    if (row != 3U || bit >= 64U) return 6U;
    mask = 1U << (bit & 31U);
    if (enabled != 0U) open_cfw_mode1_fixture_bitmap[bit >> 5] |= mask;
    else open_cfw_mode1_fixture_bitmap[bit >> 5] &= ~mask;
    return 0U;
}

uint32_t open_cfw_mode1_host_bitmap_any(uint32_t row)
{
    return row == 3U && (open_cfw_mode1_fixture_bitmap[0] | open_cfw_mode1_fixture_bitmap[1]) != 0U;
}

uint32_t open_cfw_mode1_host_critical_save(void)
{
    ++open_cfw_mode1_fixture_save_calls;
    return 0x55U;
}

void open_cfw_mode1_host_critical_restore(uint32_t mask)
{
    if (mask == 0x55U) ++open_cfw_mode1_fixture_restore_calls;
}

uint32_t open_cfw_mode1_host_control(uint32_t request, uint32_t value)
{
    ++open_cfw_mode1_fixture_control_calls;
    open_cfw_mode1_fixture_control_request = request;
    open_cfw_mode1_fixture_control_value = value;
    return 0xDEADU;
}

void open_cfw_mode1_host_poll_delay(uint32_t *remaining, uint8_t *active)
{
    ++open_cfw_mode1_fixture_poll_calls;
    open_cfw_mode1_fixture_poll_remaining = remaining;
    if (*remaining != 0U && *active != 0U) --*remaining;
}

#include "../../components/bootloader/core_overlay/runtime_mode1_services_421b08.c"

void open_cfw_mode1_fixture_reset(void)
{
    open_cfw_mode1_host_controller = 0U;
    open_cfw_mode1_host_enable_word = 0x1234567FU;
    open_cfw_mode1_host_disable_word = 0x89ABCDEFU;
    open_cfw_mode1_host_active = 0U;
    open_cfw_mode1_host_state = 0U;
    open_cfw_mode1_fixture_bitmap[0] = 0U;
    open_cfw_mode1_fixture_bitmap[1] = 0U;
    open_cfw_mode1_fixture_save_calls = 0U;
    open_cfw_mode1_fixture_restore_calls = 0U;
    open_cfw_mode1_fixture_control_calls = 0U;
    open_cfw_mode1_fixture_control_request = 0U;
    open_cfw_mode1_fixture_control_value = 0U;
    open_cfw_mode1_fixture_update_calls = 0U;
    open_cfw_mode1_fixture_update_bit = 0U;
    open_cfw_mode1_fixture_update_enabled = 0U;
    open_cfw_mode1_fixture_poll_calls = 0U;
    open_cfw_mode1_fixture_poll_remaining = 0;
}
