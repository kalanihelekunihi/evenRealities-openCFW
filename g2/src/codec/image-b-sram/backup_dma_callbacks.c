/* SPDX-License-Identifier: MIT
 * Image-B DMA callback slots at 0x10004cb8. The native body writes the
 * handler and its context to adjacent words in the same channel record.
 */
#include <stdint.h>

void gx8002_image_b_dma_callback_10004cb8(uint32_t channel,
                                           uintptr_t callback,
                                           uintptr_t context)
{
    volatile uintptr_t *slot = (volatile uintptr_t *)(uintptr_t)UINT32_C(0x200174a8);
    slot[channel] = callback;
    slot[channel + 2u] = context;
}
