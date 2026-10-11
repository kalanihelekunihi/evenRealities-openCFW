/* SPDX-License-Identifier: MIT
 * Image-B audio capture setup 0x100055e0. Native C-SKY word stores establish
 * the five separate control-register updates and SRAM status bit.
 * The native DIVU divisor is a caller precondition: frame_quantum != 0.
 */
#include <stdint.h>

#define CAP_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0a00000) + (offset)))
#define CAP_STATE_WORD (*(volatile uint32_t *)(uintptr_t)UINT32_C(0x20017628))

uint32_t gx8002_image_b_audio_capture_setup_100055e0(
    uint32_t buffer, uint32_t bytes, uint32_t frame_quantum,
    uint32_t first_mode, uint32_t second_mode)
{
    if ((buffer & 7u) != 0u || (bytes % 80u) != 0u ||
        (bytes % frame_quantum) != 0u) {
        return UINT32_MAX;
    }
    uint32_t frames = bytes / 80u;
    CAP_WORD(0x108u) = (CAP_WORD(0x108u) & ~(3u << 19)) |
                       ((first_mode & 3u) << 19);
    CAP_WORD(0x108u) = (CAP_WORD(0x108u) & ~(7u << 16)) |
                       ((second_mode & 7u) << 16);
    CAP_WORD(0x15cu) = frame_quantum;
    CAP_WORD(0x160u) = buffer & ~7u;
    CAP_WORD(0x164u) = frames * 80u;
    CAP_WORD(0x104u) = 8192u;
    CAP_WORD(0x108u) = CAP_WORD(0x108u) | (1u << 22);
    CAP_WORD(0x108u) = CAP_WORD(0x108u) & ~(1u << 23);
    CAP_WORD(0x108u) = CAP_WORD(0x108u) | (1u << 21);
    CAP_STATE_WORD = CAP_STATE_WORD | 4u;
    return 0u;
}
