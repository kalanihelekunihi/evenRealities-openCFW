/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "../../components/bootloader/core_overlay/runtime_row4_disable_421e4a.c"

uint8_t open_cfw_row4_disable_host_active;
uint32_t *open_cfw_row4_disable_host_state_pointer;
uint32_t open_cfw_row4_disable_fixture_bitmap[2];
uint32_t open_cfw_row4_disable_fixture_switch_calls;
uint32_t open_cfw_row4_disable_fixture_restore_calls;
uint32_t open_cfw_row4_disable_fixture_poll_calls;
uint32_t open_cfw_row4_disable_host_bitmap_any(uint32_t row) { return row == 4U && (open_cfw_row4_disable_fixture_bitmap[0] | open_cfw_row4_disable_fixture_bitmap[1]) != 0U; }
uint32_t open_cfw_row4_disable_host_bitmap_test(uint32_t row, uint32_t bit) { return row == 4U && bit < 64U ? (open_cfw_row4_disable_fixture_bitmap[bit >> 5] >> (bit & 31U)) & 1U : 0U; }
uint32_t open_cfw_row4_disable_host_bitmap_update(uint32_t row, uint32_t bit, uint32_t set) { if (row != 4U || bit >= 64U) return 2U; if (set) open_cfw_row4_disable_fixture_bitmap[bit >> 5] |= 1U << (bit & 31U); else open_cfw_row4_disable_fixture_bitmap[bit >> 5] &= ~(1U << (bit & 31U)); return 0U; }
void open_cfw_row4_disable_host_poll(uint32_t *remaining) { ++open_cfw_row4_disable_fixture_poll_calls; *(volatile uint8_t *)remaining = 0U; }
uint32_t open_cfw_row4_disable_host_critical_save(void) { return 0x3CU; }
void open_cfw_row4_disable_host_critical_restore(uint32_t mask) { if (mask == 0x3CU) ++open_cfw_row4_disable_fixture_restore_calls; }
uint32_t open_cfw_row4_disable_host_switch(uint32_t value) { (void)value; ++open_cfw_row4_disable_fixture_switch_calls; return 0U; }
void open_cfw_row4_disable_fixture_reset(void) { open_cfw_row4_disable_host_active = 0U; open_cfw_row4_disable_host_state_pointer = 0; open_cfw_row4_disable_fixture_bitmap[0] = 0U; open_cfw_row4_disable_fixture_bitmap[1] = 0U; open_cfw_row4_disable_fixture_switch_calls = 0U; open_cfw_row4_disable_fixture_restore_calls = 0U; open_cfw_row4_disable_fixture_poll_calls = 0U; }
