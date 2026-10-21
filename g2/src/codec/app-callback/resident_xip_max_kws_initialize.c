/* SPDX-License-Identifier: MIT
 * Native XIP 0x10208944/78; literal 0x1020895c=0x2002e744,
 * and 0x10208960 points to the exact stock diagnostic string.
 * Strategy reset 0x10208964 is already selected source.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern void gx8002_xip_kws_strategy_reset_10208964(void);

void gx8002_xip_kws_strategy_initialize_10208978(void)
{
    gx8002_xip_kws_strategy_reset_10208964();
}

void gx8002_xip_max_kws_initialize_10208944(void)
{
    const volatile uint32_t *const state =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e744);
    if (state[0x58u / 4u] != 2u)
        (void)gx8002_xip_tws_publish_10206c24(
            "[LVP_MAX_DECODE]==ERROR== The activation_flag space is too small\n");
    gx8002_xip_kws_strategy_initialize_10208978();
}
