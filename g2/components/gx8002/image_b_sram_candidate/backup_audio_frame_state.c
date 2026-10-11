/* SPDX-License-Identifier: MIT
 * Image-B 0x10009e18..0x10009e8c audio frame-state accessors.
 * Runtime state at 0x20017700 is a separate SRAM initialization contract.
 */
#include <stdint.h>

static volatile uint32_t *const audio_state =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20017700);

uint32_t gx8002_image_b_audio_state_word_50_10009e18(void)
{
    return audio_state[0x50u / 4u];
}

uint32_t gx8002_image_b_audio_state_word_54_10009e24(void)
{
    return audio_state[0x54u / 4u];
}

uint32_t gx8002_image_b_audio_state_word_70_10009e30(void)
{
    return audio_state[0x70u / 4u];
}

uint32_t gx8002_image_b_audio_state_word_74_10009e3c(void)
{
    return audio_state[0x74u / 4u];
}

uint32_t gx8002_image_b_audio_state_address_10009e48(void)
{
    return UINT32_C(0x20017700);
}

uint32_t gx8002_image_b_audio_frame_address_10009e50(uint32_t frame)
{
    uint32_t frame_count = audio_state[0x18u / 4u];
    audio_state[0x80u / 4u] = UINT32_C(0x20017700);
    audio_state[0x90u / 4u] = UINT32_C(0x200177a0);
    if (frame_count == 0u) return 0u;
    uint32_t block_bytes = frame_count << 9;
    uint32_t pitch = block_bytes * audio_state[0x24u / 4u];
    uint32_t period = (audio_state[0x34u / 4u] * block_bytes) / pitch;
    uint32_t selected = frame - (frame / period) * period;
    return audio_state[0x48u / 4u] + selected * pitch;
}

uint32_t gx8002_image_b_audio_frame_slot_10009e8c(
    uint32_t index, uint32_t *address, uint32_t *size)
{
    uint32_t slot_address = UINT32_C(0x20017780) +
                            (index & 3u) * 0xb00u;
    volatile uint32_t *const slot =
        (volatile uint32_t *)(uintptr_t)slot_address;
    slot[0] = UINT32_C(0x20017700);
    slot[0x10u / 4u] = slot_address + 0x20u;
    *address = slot_address;
    *size = 0xb00u;
    return 0u;
}
