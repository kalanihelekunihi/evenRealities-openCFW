/* SPDX-License-Identifier: MIT
 * Image-B audio mode 0x10005ec8 and its authenticated indirect tail
 * 0x10005f04..0x10005ff0. The eight immediate mode command words are
 * semantic hardware values from native branch targets, not code bytes.
 */
#include <stdint.h>

#define MODE_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0b00000) + (offset)))

static void pulse_mode_bit(void)
{
    MODE_WORD(0x28u) = MODE_WORD(0x28u) | 2u;
    MODE_WORD(0x28u) = MODE_WORD(0x28u) & ~2u;
}

void gx8002_image_b_audio_mode_10005ec8(void)
{
    static const uint16_t command_for_mode[8] = {
        2693u, 2437u, 2181u, 2949u, 2565u, 2309u, 2053u, 3589u
    };
    MODE_WORD(0x28u) = MODE_WORD(0x28u) | 1u;
    pulse_mode_bit();
    pulse_mode_bit();
    uint32_t mode = (MODE_WORD(0x04u) >> 4) & 7u;
    MODE_WORD(0x28u) = command_for_mode[mode];
    pulse_mode_bit();
    MODE_WORD(0x28u) = 9u;
    pulse_mode_bit();
    uint32_t channel = (MODE_WORD(0x24u) << 4) & ~UINT32_C(31);
    MODE_WORD(0x28u) = channel | 5u;
    pulse_mode_bit();
    MODE_WORD(0x28u) = 14181u;
    pulse_mode_bit();
    MODE_WORD(0x28u) = channel | 21u;
    pulse_mode_bit();
    MODE_WORD(0x28u) = 14181u;
    pulse_mode_bit();
    MODE_WORD(0x28u) = 9093u;
    pulse_mode_bit();
}
