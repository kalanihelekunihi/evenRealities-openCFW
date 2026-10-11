/* SPDX-License-Identifier: MIT
 * Image-B capture-path setup 0x1000568c and I2S input setup 0x10005794.
 * Native C-SKY instructions establish every volatile store and stack argument.
 */
#include <stdint.h>

#define PATH_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0a00000) + (offset)))
#define PATH_STATE (*(volatile uint32_t *)(uintptr_t)UINT32_C(0x20017628))

extern void gx8002_image_b_platform_gate_10003be8(uint32_t module, uint32_t enabled);

static void path_field(uint32_t offset, uint32_t mask, uint32_t value)
{
    PATH_WORD(offset) = (PATH_WORD(offset) & ~mask) | (value & mask);
}

uint32_t gx8002_image_b_pcm_path_1000568c(
    uint32_t channel, uint32_t address, uint32_t bytes,
    uint32_t frames, uint32_t word_mode, uint32_t output_mode)
{
    /* Native writes output_mode before rejecting address, size or channel. */
    path_field(0x108u, 7u << 16, (output_mode & 7u) << 16);
    if ((bytes & 127u) != 0u || (address & 7u) != 0u)
        return UINT32_MAX;
    if (channel == 1u) {
        PATH_WORD(0x110u) = frames * 2u;
        PATH_WORD(0x114u) = address;
        PATH_WORD(0x11cu) = 0u;
        PATH_WORD(0x120u) = bytes;
        PATH_WORD(0x104u) = 0x800u;
        path_field(0x108u, 3u, 3u);
        path_field(0x108u, 3u << 2, (word_mode & 3u) << 2);
        path_field(0x108u, 1u << 6, 1u << 6);
        path_field(0x108u, 1u << 7, 0u);
        path_field(0x108u, 1u << 5, 1u << 5);
    } else if (channel == 2u) {
        PATH_WORD(0x134u) = frames * 2u;
        PATH_WORD(0x138u) = address;
        PATH_WORD(0x140u) = 0u;
        PATH_WORD(0x144u) = bytes;
        PATH_WORD(0x104u) = 0x1000u;
        path_field(0x108u, 3u << 8, 3u << 8);
        path_field(0x108u, 3u << 10, (word_mode & 3u) << 10);
        path_field(0x108u, 1u << 14, 1u << 14);
        path_field(0x108u, 1u << 15, 0u);
        path_field(0x108u, 1u << 13, 1u << 13);
    } else {
        return UINT32_MAX;
    }
    PATH_STATE = PATH_STATE | channel;
    return 0u;
}

uint32_t gx8002_image_b_i2s_input_10005794(
    uint32_t pcm_length, uint32_t data_format, uint32_t clock_mode,
    uint32_t fsync_mode, uint32_t bclk_mode,
    uint32_t left_source, uint32_t right_source)
{
    gx8002_image_b_platform_gate_10003be8(2u, 1u);
    if (fsync_mode >= 2u || data_format >= 3u || pcm_length == 8u)
        return UINT32_MAX;
    path_field(0x08u, 3u, pcm_length & 3u);
    path_field(0x08u, 3u << 2, (data_format & 3u) << 2);
    path_field(0x08u, 1u << 4, (clock_mode & 1u) << 4);
    path_field(0x08u, 1u << 5, (fsync_mode & 1u) << 5);
    path_field(0x08u, 3u << 6, (bclk_mode & 3u) << 6);
    path_field(0x08u, 15u << 8, (left_source & 15u) << 8);
    path_field(0x08u, 15u << 12, (right_source & 15u) << 12);
    path_field(0x08u, 1u << 31, 0u);
    path_field(0x08u, 1u << 30, 1u << 30);
    PATH_STATE = PATH_STATE | 8u;
    path_field(0x08u, 1u << 16, 1u << 16);
    return 0u;
}
