/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "../../components/bootloader/core_overlay/runtime_mode0_disable_421cce.c"

uint8_t open_cfw_mode0_disable_host_active;
uint8_t open_cfw_mode0_disable_host_complete;
uint32_t *open_cfw_mode0_disable_host_state_pointer;
uint32_t open_cfw_mode0_disable_fixture_bitmap[2];
uint32_t open_cfw_mode0_disable_fixture_control_request;
uint32_t open_cfw_mode0_disable_fixture_control_argument;
uint32_t open_cfw_mode0_disable_fixture_control_calls;
uint32_t open_cfw_mode0_disable_fixture_restore_calls;
uint32_t open_cfw_mode0_disable_fixture_poll_calls;

uint32_t open_cfw_mode0_disable_host_bitmap_any(uint32_t row) {
    return row == 2U && (open_cfw_mode0_disable_fixture_bitmap[0] | open_cfw_mode0_disable_fixture_bitmap[1]) != 0U;
}
uint32_t open_cfw_mode0_disable_host_bitmap_test(uint32_t row, uint32_t bit) {
    if (row != 2U || bit >= 64U) return 0U;
    return (open_cfw_mode0_disable_fixture_bitmap[bit >> 5] >> (bit & 31U)) & 1U;
}
uint32_t open_cfw_mode0_disable_host_bitmap_update(uint32_t row, uint32_t bit, uint32_t set) {
    if (row != 2U || bit >= 64U) return 2U;
    if (set != 0U) open_cfw_mode0_disable_fixture_bitmap[bit >> 5] |= 1U << (bit & 31U);
    else open_cfw_mode0_disable_fixture_bitmap[bit >> 5] &= ~(1U << (bit & 31U));
    return 0U;
}
void open_cfw_mode0_disable_host_poll(uint32_t *remaining) {
    ++open_cfw_mode0_disable_fixture_poll_calls;
    *(volatile uint8_t *)remaining = 0U;
}
uint32_t open_cfw_mode0_disable_host_critical_save(void) { return 0xA5U; }
void open_cfw_mode0_disable_host_critical_restore(uint32_t mask) {
    if (mask == 0xA5U) ++open_cfw_mode0_disable_fixture_restore_calls;
}
uint32_t open_cfw_mode0_disable_host_control(uint32_t request, uint8_t *argument) {
    ++open_cfw_mode0_disable_fixture_control_calls;
    open_cfw_mode0_disable_fixture_control_request = request;
    open_cfw_mode0_disable_fixture_control_argument = argument == 0 ? 0U : *argument;
    return 0U;
}
void open_cfw_mode0_disable_fixture_reset(void) {
    open_cfw_mode0_disable_host_active = 0U;
    open_cfw_mode0_disable_host_complete = 0U;
    open_cfw_mode0_disable_host_state_pointer = 0;
    open_cfw_mode0_disable_fixture_bitmap[0] = 0U;
    open_cfw_mode0_disable_fixture_bitmap[1] = 0U;
    open_cfw_mode0_disable_fixture_control_request = 0U;
    open_cfw_mode0_disable_fixture_control_argument = 0U;
    open_cfw_mode0_disable_fixture_control_calls = 0U;
    open_cfw_mode0_disable_fixture_restore_calls = 0U;
    open_cfw_mode0_disable_fixture_poll_calls = 0U;
}
