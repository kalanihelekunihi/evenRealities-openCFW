/* SPDX-License-Identifier: MIT
 * Image-B audio channel routing 0x10005490 and dual-buffer setup 0x100054cc.
 * The C-SKY source has two channel envelopes and seventh stack argument.
 */
#include <stdint.h>

#define BUFFER_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0a00000) + (offset)))
#define BUFFER_STATE (*(volatile uint32_t *)(uintptr_t)UINT32_C(0x20017628))

static void buffer_field(uint32_t offset, uint32_t mask, uint32_t value)
{
    BUFFER_WORD(offset) = (BUFFER_WORD(offset) & ~mask) | (value & mask);
}

uint32_t gx8002_image_b_channel_sources_10005490(
    uint32_t channel, uint32_t left, uint32_t right)
{
    if (channel == 2u) {
        buffer_field(0x28u, 15u, left);
        buffer_field(0x2cu, 15u, right);
    } else if (channel == 4u) {
        buffer_field(0x48u, 15u, left);
        buffer_field(0x4cu, 15u, right);
    }
    return 0u;
}

uint32_t gx8002_image_b_dual_buffer_100054cc(
    uint32_t channel, uint32_t left, uint32_t right,
    uint32_t bytes, uint32_t frame_count,
    uint32_t endian, uint32_t source)
{
    if ((channel != 1u && channel != 2u) || (bytes & 127u) != 0u ||
        ((left | right) & 7u) != 0u)
        return UINT32_MAX;
    if (channel == 1u) {
        BUFFER_WORD(0x110u) = frame_count;
        BUFFER_WORD(0x114u) = left;
        BUFFER_WORD(0x11cu) = right;
        BUFFER_WORD(0x120u) = bytes;
        BUFFER_WORD(0x104u) = 0x800u;
        buffer_field(0x108u, 3u, source);
        buffer_field(0x108u, 3u << 2, (endian & 3u) << 2);
        buffer_field(0x108u, 1u << 6, 1u << 6);
        buffer_field(0x108u, 1u << 7, 0u);
        buffer_field(0x108u, 1u << 5, 1u << 5);
    } else {
        BUFFER_WORD(0x134u) = frame_count;
        BUFFER_WORD(0x138u) = left;
        BUFFER_WORD(0x140u) = right;
        BUFFER_WORD(0x144u) = bytes;
        BUFFER_WORD(0x104u) = 0x1000u;
        buffer_field(0x108u, 3u << 8, (source & 3u) << 8);
        buffer_field(0x108u, 3u << 10, (endian & 3u) << 10);
        buffer_field(0x108u, 1u << 14, 1u << 14);
        buffer_field(0x108u, 1u << 15, 0u);
        buffer_field(0x108u, 1u << 13, 1u << 13);
    }
    BUFFER_STATE = BUFFER_STATE | channel;
    return 0u;
}
