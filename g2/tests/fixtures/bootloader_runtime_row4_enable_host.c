/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "../../components/bootloader/core_overlay/runtime_row4_enable_421d5e.c"

uint8_t open_cfw_row4_host_active;
uint8_t open_cfw_row4_host_ready;
uint8_t open_cfw_row4_host_complete;
uint32_t open_cfw_row4_host_current;
uint32_t open_cfw_row4_host_configuration;
uint32_t *open_cfw_row4_host_state_pointer;
uint32_t open_cfw_row4_fixture_bitmap[2];
uint32_t open_cfw_row4_fixture_switch_calls;
uint32_t open_cfw_row4_fixture_switch_value;
uint32_t open_cfw_row4_fixture_apply_calls;
uint32_t open_cfw_row4_fixture_apply_status;
uint32_t open_cfw_row4_fixture_update_calls;
uint32_t open_cfw_row4_fixture_restore_calls;
uint32_t open_cfw_row4_fixture_cleanup_value;

uint32_t open_cfw_row4_host_bitmap_test(uint32_t row, uint32_t bit) {
    return row == 4U && bit < 64U ? (open_cfw_row4_fixture_bitmap[bit >> 5] >> (bit & 31U)) & 1U : 0U;
}
uint32_t open_cfw_row4_host_bitmap_count(uint32_t row) {
    uint32_t x, count = 0U;
    if (row != 4U) return 0U;
    x = open_cfw_row4_fixture_bitmap[0] | open_cfw_row4_fixture_bitmap[1];
    while (x != 0U) { count += x & 1U; x >>= 1; }
    return count;
}
uint32_t open_cfw_row4_host_bitmap_update(uint32_t row, uint32_t bit, uint32_t set) {
    ++open_cfw_row4_fixture_update_calls;
    if (row != 4U || bit >= 64U) return 2U;
    if (set != 0U) open_cfw_row4_fixture_bitmap[bit >> 5] |= 1U << (bit & 31U);
    else open_cfw_row4_fixture_bitmap[bit >> 5] &= ~(1U << (bit & 31U));
    return 0U;
}
uint32_t open_cfw_row4_host_critical_save(void) { return 0x5AU; }
void open_cfw_row4_host_critical_restore(uint32_t mask) { if (mask == 0x5AU) ++open_cfw_row4_fixture_restore_calls; }
void open_cfw_row4_host_cleanup(uint32_t *remaining) { open_cfw_row4_fixture_cleanup_value = *remaining; }
uint32_t open_cfw_row4_host_switch(uint32_t value) { ++open_cfw_row4_fixture_switch_calls; open_cfw_row4_fixture_switch_value = value; return 0U; }
uint32_t open_cfw_row4_host_apply(uint32_t value) { ++open_cfw_row4_fixture_apply_calls; (void)value; return open_cfw_row4_fixture_apply_status; }
void open_cfw_row4_fixture_reset(void) {
    open_cfw_row4_host_active = 0U; open_cfw_row4_host_ready = 1U;
    open_cfw_row4_host_complete = 0U; open_cfw_row4_host_current = 1U;
    open_cfw_row4_host_configuration = 0x1234U; open_cfw_row4_host_state_pointer = 0;
    open_cfw_row4_fixture_bitmap[0] = 0U; open_cfw_row4_fixture_bitmap[1] = 0U;
    open_cfw_row4_fixture_switch_calls = 0U; open_cfw_row4_fixture_switch_value = 0U;
    open_cfw_row4_fixture_apply_calls = 0U; open_cfw_row4_fixture_apply_status = 0U;
    open_cfw_row4_fixture_update_calls = 0U; open_cfw_row4_fixture_restore_calls = 0U;
    open_cfw_row4_fixture_cleanup_value = 0U;
}
