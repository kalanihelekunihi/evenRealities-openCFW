/* SPDX-License-Identifier: MIT
 * Native image-B 0x10005e9c..0x10005ec5. Ghidra ended at the MMIO
 * wait; the authenticated branch continues to the final two writes.
 */
#include <stdint.h>

#define START_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0b00000) + (offset)))

void gx8002_image_b_audio_start_10005e9c(void)
{
    START_WORD(0x0cu) = START_WORD(0x0cu) | UINT32_C(0x00400000);
    while ((START_WORD(0x0cu) & UINT32_C(0x00100000)) == 0u) { }
    START_WORD(0x0cu) = START_WORD(0x0cu) & UINT32_C(0x00100000);
    START_WORD(0x00u) = START_WORD(0x00u) | UINT32_C(0x80000000);
}
