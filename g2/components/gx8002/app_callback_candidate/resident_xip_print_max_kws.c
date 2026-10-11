/* SPDX-License-Identifier: MIT
 * Native XIP 0x10208880..0x102088d9. Printed strings and the two-keyword
 * descriptor pointer are authenticated literals. Actual 0x20026c7c KWS
 * product records still require source-owned initialized-data attribution.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);

void gx8002_xip_print_max_kws_list_10208880(void)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e744);
    state[0x58u / 4u] = 2u;
    state[0x5cu / 4u] = UINT32_C(0x20026c7c);
    (void)gx8002_xip_tws_publish_10206c24(
        "[LVP_MAX_DECODE]Demo Kws List [Total:%d]:\n", 2);
    for (uint32_t index = 0; index < state[0x58u / 4u]; ++index) {
        const uint8_t *entry = (const uint8_t *)(uintptr_t)
            (state[0x5cu / 4u] + index * 0x58u);
        (void)gx8002_xip_tws_publish_10206c24(
            "[LVP_MAX_DECODE]KWS: %s | ", (const char *)entry);
        (void)gx8002_xip_tws_publish_10206c24(
            "KV: %02d | ", *(const int32_t *)(const void *)(entry + 0x50u));
        (void)gx8002_xip_tws_publish_10206c24(
            "TRH: %02d | ", *(const int32_t *)(const void *)(entry + 0x4cu));
        (void)gx8002_xip_tws_publish_10206c24("\n");
    }
}
