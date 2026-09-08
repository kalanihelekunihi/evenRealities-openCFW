/* SPDX-License-Identifier: MIT */
/* Recovered from image-A startup queries. Numeric reason codes preserve the
 * shipped priority order; hardware meanings beyond the SDK mode enum are not
 * inferred. MMIO reads, including the discarded final read, are observable. */
#include <stdint.h>

__attribute__((noinline)) unsigned int open_cfw_gx8002_reset_reason(void)
{
    const uint32_t status = *(volatile uint32_t *)0xa0000034u;
    if (status & 1u) return 2;
    if (status & 4u) return 3;
    if (status & 8u) return 5;
    if (status & 2u) return 4;
    return *(volatile uint32_t *)0xa001002cu & 1u;
}

int open_cfw_gx8002_start_mode(void)
{
    unsigned int reason = open_cfw_gx8002_reset_reason();
    if (reason - 2u >= 4u) return 0;
    unsigned int mode = *(volatile uint32_t *)0xa0010058u & 1u;
    (void)*(volatile uint32_t *)0xa001005cu;
    return (int)mode;
}
