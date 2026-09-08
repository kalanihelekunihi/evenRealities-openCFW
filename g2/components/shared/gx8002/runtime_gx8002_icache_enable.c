/* SPDX-License-Identifier: MIT */
/* GX8002 external instruction-cache controller, distinct from CSI CACHE.
 * Decoded from the authenticated gx_icache_enable SDK/firmware match.
 * Preserve the original unbounded ready poll; no timeout policy is inferred.
 */
#include <stdint.h>

void gx_icache_enable(void)
{
    volatile uint32_t *controller = (volatile uint32_t *)0xB0000000U;
    controller[0] = 0;
    controller[0] |= 1U;
    while ((controller[1] & 3U) != 2U) {
    }
}
