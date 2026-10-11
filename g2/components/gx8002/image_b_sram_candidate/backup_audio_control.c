/* SPDX-License-Identifier: MIT
 * Image-B native audio-control leaves 0x10005cb0 and 0x10005cbc.
 * Native MOVIH 0xa0a0 resolves these words to the audio MMIO block.
 */
#include <stdint.h>

#define AUDIO_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0a00000) + (offset)))

uint32_t gx8002_image_b_audio_read_status_10005cb0(void)
{
    return AUDIO_WORD(0x1b8u);
}

int32_t gx8002_image_b_audio_update_mask_10005cbc(
    uint32_t mask, int32_t enable)
{
    if (enable == 0) {
        AUDIO_WORD(0x100u) = AUDIO_WORD(0x100u) & ~mask;
        AUDIO_WORD(0x104u) = mask;
        return 0;
    }
    AUDIO_WORD(0x104u) = mask;
    AUDIO_WORD(0x100u) = mask | AUDIO_WORD(0x100u);
    return 0;
}
