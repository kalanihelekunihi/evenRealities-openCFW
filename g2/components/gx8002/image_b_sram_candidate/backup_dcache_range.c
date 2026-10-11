/* SPDX-License-Identifier: MIT
 * Image-B cache-line range commands 0x10004dd8 and 0x10004e74.
 * Both native loops issue 16-byte line addresses to 0xe000f004, in eight
 * unrolled writes for each complete 128-byte block. Command bits differ.
 */
#include <stdint.h>

#ifdef GX8002_IMAGE_B_CACHE_TRACE
extern void gx8002_image_b_cache_trace_emit(uint32_t command);
#define CACHE_EMIT(value) gx8002_image_b_cache_trace_emit(value)
#else
#define CACHE_EMIT(value) (*line_command = (value))
#endif

static void cache_range(uint32_t address, int32_t length, uint32_t command)
{
#ifndef GX8002_IMAGE_B_CACHE_TRACE
    volatile uint32_t *line_command =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f004);
#endif
    uint32_t line = (address & ~UINT32_C(15)) | command;
    if (length >= 128) {
        uint32_t remaining_after_first = (uint32_t)length - 128u;
        uint32_t extra_blocks = remaining_after_first & ~UINT32_C(127);
        uint32_t end = line + extra_blocks + 128u;
        do {
            for (uint32_t offset = 0u; offset < 128u; offset += 16u)
                CACHE_EMIT(line + offset);
            line += 128u;
        } while (line != end);
        length = (int32_t)(remaining_after_first - extra_blocks);
    }
    if (length > 0) {
        uint32_t end = line + 16u + (((uint32_t)length - 1u) & ~UINT32_C(15));
        uint32_t next = line + 16u;
        do {
            CACHE_EMIT(line);
            line = next;
            if (next == end) break;
            next += 16u;
        } while (1);
    }
}

void gx8002_image_b_dcache_invalidate_range_10004dd8(uint32_t address, int32_t length)
{
    cache_range(address, length, 2u);
}

void gx8002_image_b_dcache_clean_range_10004e74(uint32_t address, int32_t length)
{
    cache_range(address, length, 8u);
}

void gx8002_image_b_dcache_clean_invalidate_range_10004f10(
    uint32_t address, int32_t length)
{
    cache_range(address, length, 10u);
}
