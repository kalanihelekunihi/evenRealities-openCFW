/* SPDX-License-Identifier: MIT
 * Image-B flash interrupt 0x10007138. Native reads status once and reads
 * the two acknowledgement registers conditionally; Ghidra omitted the
 * volatile reads because their values are not returned.
 */
#include <stdint.h>

uint32_t gx8002_image_b_flash_interrupt_10007138(void)
{
    volatile uint32_t *flash =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    uint32_t status = flash[0x30u / 4u];
    if ((status & 2u) != 0u) (void)flash[0x38u / 4u];
    if ((status & 8u) != 0u) (void)flash[0x3cu / 4u];
    return 0u;
}
