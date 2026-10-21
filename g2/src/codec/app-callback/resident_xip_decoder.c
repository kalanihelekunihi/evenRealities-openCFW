/* SPDX-License-Identifier: MIT
 * Image-A XIP 0x102088f8 maximum-decoder dispatch and 0x10208964
 * strategy reset. Native destinations and call order are source-bound;
 * scoring and strategy selection remain genuine XIP lower contracts.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_max_score_102086dc(void *record, uint32_t mode);
extern const uint8_t *gx8002_xip_kws_strategy_10208a10(void *record);
extern void gx8002_xip_ctc_offset_clear_10208b64(void);
extern void gx8002_xip_memset_102099cc(void *, uint32_t, uint32_t);

/* Native 0x10208964 calls memset(0x2002e7a8, 0, 164). */
void gx8002_xip_kws_strategy_reset_10208964(void)
{
    gx8002_xip_memset_102099cc(
        (void *)(uintptr_t)UINT32_C(0x2002e7a8), 0u, 164u);
}

/* The earlier import name says "tws_event"; 0x102088f8 is actually the
 * maximum-decoder root called with a mutable decoder event pointer. */
uint32_t gx8002_xip_tws_event_102088f8(void *record)
{
    if (gx8002_xip_max_score_102086dc(record, 1u) != 0u) {
        volatile const uint32_t *const status =
            (volatile const uint32_t *)(uintptr_t)UINT32_C(0x20026d2c);
        if (*status == 1u)
            (void)gx8002_xip_max_score_102086dc(record, 0u);
    }
    volatile uint32_t *const count =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e748);
    *count = *count + 1u;
    const uint8_t *selection = gx8002_xip_kws_strategy_10208a10(record);
    if (selection != 0) {
        ((uint8_t *)record)[0x0du] = selection[4];
        gx8002_xip_ctc_offset_clear_10208b64();
        gx8002_xip_kws_strategy_reset_10208964();
    }
    return 0u;
}
