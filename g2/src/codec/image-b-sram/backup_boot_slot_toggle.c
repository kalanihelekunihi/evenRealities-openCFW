/* SPDX-License-Identifier: MIT
 * Image-B 0x1000aad0. Native literal 0x20033ffc is the slot marker and
 * 0xaabbccdd is its second-slot value; the two logger strings are exact
 * source-owned data at 0x100135ec and 0x10013608.
 */
#include <stdint.h>

extern int gx8002_image_b_heap_log_10009934(const char *, ...);
extern void gx8002_image_b_dcache_clean_range_10004e74(uint32_t, int32_t);
extern __attribute__((noreturn)) void gx8002_image_b_reset_policy_10008868(void);

void gx8002_image_b_boot_slot_toggle_1000aad0(void)
{
    volatile uint32_t *const marker =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20033ffc);
    if (*marker == UINT32_C(0xaabbccdd)) {
        (void)gx8002_image_b_heap_log_10009934(
            "boot from first firmware\n");
        *marker = 0u;
    } else {
        (void)gx8002_image_b_heap_log_10009934(
            "boot from second firmware\n");
        *marker = UINT32_C(0xaabbccdd);
    }
    gx8002_image_b_dcache_clean_range_10004e74(
        UINT32_C(0x20033ffc), 16);
    gx8002_image_b_reset_policy_10008868();
}
