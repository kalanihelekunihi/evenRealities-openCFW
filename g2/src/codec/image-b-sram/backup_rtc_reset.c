/* SPDX-License-Identifier: MIT
 * Image-B RTC tick start 0x10008800 and native reset policy 0x10008868.
 */
#include <stdint.h>

extern void gx8002_image_b_platform_gate_10003be8(
    uint32_t module, uint32_t enabled);

typedef uint32_t (*rtc_callback)(uint32_t irq, uint32_t context);

uint32_t gx8002_image_b_rtc_irq_100087dc(uint32_t irq)
{
    volatile const uint32_t *const callback_state =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x200176d0);
    volatile const uint32_t *const rtc =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0xa0003000);
    rtc_callback callback = (rtc_callback)(uintptr_t)callback_state[0];
    uint32_t result = 0u;
    if (callback != (rtc_callback)0)
        result = callback(irq, callback_state[1]);
    (void)rtc[0x18u / 4u];
    return result;
}

/* Stock 0x10008800 (gx_rtc_start_tick) */
void gx8002_image_b_rtc_start_tick_10008800(void)
{
    volatile uint32_t *const rtc =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0003000);
    rtc[0x0cu / 4u] |= 4u;
}

void gx8002_image_b_rtc_write_control_10008810(uint32_t value)
{
    volatile uint32_t *const rtc =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0003000);
    rtc[0x08u / 4u] = value;
}

__attribute__((noreturn)) void gx8002_image_b_reset_policy_10008868(void)
{
    volatile uint32_t *const gate =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010000);
    volatile uint32_t *const reset =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0700000);
    gx8002_image_b_platform_gate_10003be8(24u, 1u);
    gate[0x2cu / 4u] = 1u;
    reset[0] = 0u;
    reset[1] = 0u;
    reset[3] = 118u;
    reset[0] = 1u;
    for (;;) { }
}
