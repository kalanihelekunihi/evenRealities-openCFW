/* SPDX-License-Identifier: MIT
 * Image-A SRAM KWS/queue leaves 0x100260d0, 0x10026340,
 * 0x100263b4, and 0x100263c4. Runtime callback and queue storage lie
 * inside the authenticated BSS span, with no synthesized handlers.
 */
#include <stdint.h>

extern uint32_t g2_codec_queue_enqueue(void *, const void *);
typedef void (*gx8002_kws_callback)(uint32_t, uint32_t, uint32_t);

uint32_t gx8002_resident_kws_pair_260d0(
    uint32_t arg0, uint32_t arg1, uint32_t arg2)
{
    const volatile uint32_t *const callback_slot =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x20027b50);
    uint32_t raw = *callback_slot;
    if (raw != 0u && arg2 != 0u)
        ((gx8002_kws_callback)(uintptr_t)raw)(arg0, arg1, arg2);
    return 0u;
}

/* Stock 0x10026340 (gx8002_active_snpu_callback) */
uint32_t gx8002_resident_active_snpu_callback_26340(
    uint32_t first, uint32_t ignored, uint32_t third)
{
    (void)ignored;
    const uint32_t pair[2] = {first, third};
    (void)g2_codec_queue_enqueue(
        (void *)(uintptr_t)UINT32_C(0x2002e6ec), pair);
    return 0u;
}

/* Stock 0x100263B4 (gx8002_tws_set_standby) */
void gx8002_resident_tws_set_standby_263b4(uint32_t state)
{
    volatile uint32_t *const queue =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e6ec);
    queue[0x4cu / 4u] = state;
    if (state == 2u) queue[0x50u / 4u] = 50u;
}

/* Stock 0x100263C4 (gx8002_tws_standby_loop) */
void gx8002_resident_tws_standby_loop_263c4(void)
{
    volatile uint32_t *const queue =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e6ec);
    if (queue[0x4cu / 4u] != 2u) return;
    uint32_t remaining = queue[0x50u / 4u] - 1u;
    queue[0x50u / 4u] = remaining;
    if (remaining == 0u) queue[0x4cu / 4u] = 4u;
}

/* 0x100264dc is a native literal-return getter for the BSS keyword list. */
/* Stock 0x100264DC (gx8002_keyword_list_get) */
void *gx8002_resident_keyword_list_get_264dc(void)
{
    return (void *)(uintptr_t)UINT32_C(0x2002e79c);
}
