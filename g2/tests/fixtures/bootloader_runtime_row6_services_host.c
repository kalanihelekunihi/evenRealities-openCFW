/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "../../components/bootloader/core_overlay/runtime_row6_services_4220b2.c"

uint8_t open_cfw_row6_host_ready, open_cfw_row6_host_selector, open_cfw_row6_host_pending;
uint32_t open_cfw_row6_host_handle, open_cfw_row6_fixture_bitmap[2];
uint32_t open_cfw_row6_fixture_enable_calls[2], open_cfw_row6_fixture_disable_calls[2];
uint32_t open_cfw_row6_fixture_create_calls, open_cfw_row6_fixture_configure_calls, open_cfw_row6_fixture_start_calls;
uint32_t open_cfw_row6_fixture_stop_calls, open_cfw_row6_fixture_destroy_calls, open_cfw_row6_fixture_finalize_calls;
uint32_t open_cfw_row6_fixture_create_status, open_cfw_row6_fixture_configure_status, open_cfw_row6_fixture_start_status, open_cfw_row6_fixture_finalize_status;
uint32_t open_cfw_row6_fixture_update_calls, open_cfw_row6_fixture_restore_calls, open_cfw_row6_fixture_dispatch_kind;

uint32_t open_cfw_row6_host_bitmap_any(uint32_t row) { return row == 6U && (open_cfw_row6_fixture_bitmap[0] | open_cfw_row6_fixture_bitmap[1]) != 0U; }
uint32_t open_cfw_row6_host_bitmap_test(uint32_t row, uint32_t bit) { return row == 6U && bit < 64U ? (open_cfw_row6_fixture_bitmap[bit >> 5] >> (bit & 31U)) & 1U : 0U; }
uint32_t open_cfw_row6_host_bitmap_count(uint32_t row) { uint32_t x, n = 0U; if (row != 6U) return 0U; x = open_cfw_row6_fixture_bitmap[0] | open_cfw_row6_fixture_bitmap[1]; while (x) { n += x & 1U; x >>= 1; } return n; }
uint32_t open_cfw_row6_host_bitmap_update(uint32_t row, uint32_t bit, uint32_t set) { ++open_cfw_row6_fixture_update_calls; if (row != 6U || bit >= 64U) return 2U; if (set) open_cfw_row6_fixture_bitmap[bit >> 5] |= 1U << (bit & 31U); else open_cfw_row6_fixture_bitmap[bit >> 5] &= ~(1U << (bit & 31U)); return 0U; }
uint32_t open_cfw_row6_host_critical_save(void) { return 0x66U; }
void open_cfw_row6_host_critical_restore(uint32_t mask) { if (mask == 0x66U) ++open_cfw_row6_fixture_restore_calls; }
uint32_t open_cfw_row6_host_mode_enable(uint8_t selector, uint32_t client) { (void)client; ++open_cfw_row6_fixture_enable_calls[selector & 1U]; return 0U; }
uint32_t open_cfw_row6_host_mode_disable(uint8_t selector, uint32_t client) { (void)client; ++open_cfw_row6_fixture_disable_calls[selector & 1U]; return 0U; }
uint32_t open_cfw_row6_host_create(uint32_t zero, uint32_t *handle) { (void)zero; ++open_cfw_row6_fixture_create_calls; if (open_cfw_row6_fixture_create_status == 0U) *handle = 0x1234U; return open_cfw_row6_fixture_create_status; }
uint32_t open_cfw_row6_host_destroy(uint32_t handle) { (void)handle; ++open_cfw_row6_fixture_destroy_calls; return 0U; }
uint32_t open_cfw_row6_host_start(uint32_t handle) { (void)handle; ++open_cfw_row6_fixture_start_calls; return open_cfw_row6_fixture_start_status; }
uint32_t open_cfw_row6_host_stop(uint32_t handle) { (void)handle; ++open_cfw_row6_fixture_stop_calls; return 0U; }
uint32_t open_cfw_row6_host_configure(uint32_t handle, uint8_t *selector) { (void)handle; (void)selector; ++open_cfw_row6_fixture_configure_calls; return open_cfw_row6_fixture_configure_status; }
uint32_t open_cfw_row6_host_finalize(uint32_t handle) { (void)handle; ++open_cfw_row6_fixture_finalize_calls; return open_cfw_row6_fixture_finalize_status; }
uint32_t open_cfw_row6_host_dispatch(uint8_t kind, uintptr_t instance, const uint32_t *configuration) { (void)instance; (void)configuration; open_cfw_row6_fixture_dispatch_kind = kind; return 0x40U + kind; }
void open_cfw_row6_fixture_reset(void) {
    open_cfw_row6_host_ready = 1U; open_cfw_row6_host_selector = 0U; open_cfw_row6_host_pending = 0U; open_cfw_row6_host_handle = 0U;
    open_cfw_row6_fixture_bitmap[0] = 0U; open_cfw_row6_fixture_bitmap[1] = 0U;
    open_cfw_row6_fixture_enable_calls[0] = 0U; open_cfw_row6_fixture_enable_calls[1] = 0U; open_cfw_row6_fixture_disable_calls[0] = 0U; open_cfw_row6_fixture_disable_calls[1] = 0U;
    open_cfw_row6_fixture_create_calls = 0U; open_cfw_row6_fixture_configure_calls = 0U; open_cfw_row6_fixture_start_calls = 0U; open_cfw_row6_fixture_stop_calls = 0U; open_cfw_row6_fixture_destroy_calls = 0U; open_cfw_row6_fixture_finalize_calls = 0U;
    open_cfw_row6_fixture_create_status = 0U; open_cfw_row6_fixture_configure_status = 0U; open_cfw_row6_fixture_start_status = 0U; open_cfw_row6_fixture_finalize_status = 0U; open_cfw_row6_fixture_update_calls = 0U; open_cfw_row6_fixture_restore_calls = 0U; open_cfw_row6_fixture_dispatch_kind = 0U;
}
