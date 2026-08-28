/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "../../components/bootloader/core_overlay/runtime_row5_services_421eba.c"

uint8_t open_cfw_row5_host_active;
uint8_t open_cfw_row5_host_ready;
uint8_t open_cfw_row5_host_pending;
uint8_t open_cfw_row5_host_selector;
uint8_t open_cfw_row5_host_controller_present;
uint32_t *open_cfw_row5_host_state_pointer;
uint32_t open_cfw_row5_fixture_bitmap[2];
uint32_t open_cfw_row5_fixture_enable_calls, open_cfw_row5_fixture_enable_status;
uint32_t open_cfw_row5_fixture_disable_calls[2];
uint32_t open_cfw_row5_fixture_switch_calls, open_cfw_row5_fixture_switch_value;
uint32_t open_cfw_row5_fixture_commit_calls, open_cfw_row5_fixture_commit_status;
uint32_t open_cfw_row5_fixture_null_commit_calls;
uint32_t open_cfw_row5_fixture_update_calls, open_cfw_row5_fixture_restore_calls;
uint32_t open_cfw_row5_fixture_cleanup_value;

uint32_t open_cfw_row5_host_bitmap_any(uint32_t row) { return row == 5U && (open_cfw_row5_fixture_bitmap[0] | open_cfw_row5_fixture_bitmap[1]) != 0U; }
uint32_t open_cfw_row5_host_bitmap_test(uint32_t row, uint32_t bit) { return row == 5U && bit < 64U ? (open_cfw_row5_fixture_bitmap[bit >> 5] >> (bit & 31U)) & 1U : 0U; }
uint32_t open_cfw_row5_host_bitmap_count(uint32_t row) {
    uint32_t x, count = 0U; if (row != 5U) return 0U;
    x = open_cfw_row5_fixture_bitmap[0] | open_cfw_row5_fixture_bitmap[1];
    while (x != 0U) { count += x & 1U; x >>= 1; } return count;
}
uint32_t open_cfw_row5_host_bitmap_update(uint32_t row, uint32_t bit, uint32_t set) {
    ++open_cfw_row5_fixture_update_calls; if (row != 5U || bit >= 64U) return 2U;
    if (set != 0U) open_cfw_row5_fixture_bitmap[bit >> 5] |= 1U << (bit & 31U);
    else open_cfw_row5_fixture_bitmap[bit >> 5] &= ~(1U << (bit & 31U)); return 0U;
}
uint32_t open_cfw_row5_host_critical_save(void) { return 0xA5U; }
void open_cfw_row5_host_critical_restore(uint32_t mask) { if (mask == 0xA5U) ++open_cfw_row5_fixture_restore_calls; }
uint32_t open_cfw_row5_host_mode_enable(uint8_t selector, uint32_t client) { (void)selector; (void)client; ++open_cfw_row5_fixture_enable_calls; return open_cfw_row5_fixture_enable_status; }
uint32_t open_cfw_row5_host_mode_disable(uint8_t selector, uint32_t client) { (void)client; if (selector < 2U) ++open_cfw_row5_fixture_disable_calls[selector]; return 0U; }
void open_cfw_row5_host_cleanup(uint32_t *remaining) { open_cfw_row5_fixture_cleanup_value = *remaining; }
uint32_t open_cfw_row5_host_switch(uint32_t value) { ++open_cfw_row5_fixture_switch_calls; open_cfw_row5_fixture_switch_value = value; return 0U; }
uint32_t open_cfw_row5_host_commit(uint8_t *selector) { (void)selector; ++open_cfw_row5_fixture_commit_calls; return open_cfw_row5_fixture_commit_status; }
uint32_t open_cfw_row5_host_null_commit(void) { ++open_cfw_row5_fixture_null_commit_calls; return 0U; }
void open_cfw_row5_fixture_reset(void) {
    open_cfw_row5_host_active = 0U; open_cfw_row5_host_ready = 1U; open_cfw_row5_host_pending = 0U;
    open_cfw_row5_host_selector = 0U; open_cfw_row5_host_controller_present = 1U; open_cfw_row5_host_state_pointer = 0;
    open_cfw_row5_fixture_bitmap[0] = 0U; open_cfw_row5_fixture_bitmap[1] = 0U;
    open_cfw_row5_fixture_enable_calls = 0U; open_cfw_row5_fixture_enable_status = 0U;
    open_cfw_row5_fixture_disable_calls[0] = 0U; open_cfw_row5_fixture_disable_calls[1] = 0U;
    open_cfw_row5_fixture_switch_calls = 0U; open_cfw_row5_fixture_switch_value = 0U;
    open_cfw_row5_fixture_commit_calls = 0U; open_cfw_row5_fixture_commit_status = 0U;
    open_cfw_row5_fixture_null_commit_calls = 0U; open_cfw_row5_fixture_update_calls = 0U;
    open_cfw_row5_fixture_restore_calls = 0U; open_cfw_row5_fixture_cleanup_value = 0U;
}
