/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-excluded clean-room expression of lv_ambiq_get_glyph().
 * Layouts are public NemaVG font ABI facts and control flow is qualified by
 * the exact AmbiqSuite 5.1.0 GCC section and DWARF.
 */

#include "runtime_ambiq_gpu_patch_get_glyph_candidate.h"

#include <stddef.h>
#include <stdint.h>

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct open_cfw_ambiq_gpu_glyph_view) == 0x24U, "glyph ABI changed");
_Static_assert(sizeof(struct open_cfw_ambiq_gpu_font_range_view) == 0x0CU, "font range ABI changed");
_Static_assert(offsetof(struct open_cfw_ambiq_gpu_font_view, ranges) == 0x04U, "font ranges offset changed");
#endif

static uint32_t open_cfw_ambiq_gpu_decode_codepoint(
    const uint8_t *utf8,
    open_cfw_ambiq_gpu_utf8_size_fn codepoint_size
)
{
    uint32_t size = codepoint_size(utf8);

    switch (size) {
        case 1U:
            return (uint32_t)(utf8[0] & 0x7FU);
        case 2U:
            return ((uint32_t)(utf8[0] & 0x1FU) << 6U) |
                   (uint32_t)(utf8[1] & 0x3FU);
        case 3U:
            return ((uint32_t)(utf8[0] & 0x0FU) << 12U) |
                   ((uint32_t)(utf8[1] & 0x3FU) << 6U) |
                   (uint32_t)(utf8[2] & 0x3FU);
        case 4U:
            return ((uint32_t)(utf8[0] & 0x07U) << 18U) |
                   ((uint32_t)(utf8[1] & 0x3FU) << 12U) |
                   ((uint32_t)(utf8[2] & 0x3FU) << 6U) |
                   (uint32_t)(utf8[3] & 0x3FU);
        default:
            return 0U;
    }
}

__attribute__((used, noinline))
const struct open_cfw_ambiq_gpu_glyph_view *
open_cfw_ambiq_gpu_get_glyph_candidate(
    const struct open_cfw_ambiq_gpu_font_view *font,
    const char *character,
    open_cfw_ambiq_gpu_utf8_size_fn codepoint_size
)
{
    const uint8_t *utf8 = (const uint8_t *)(const void *)character;
    uint32_t codepoint = open_cfw_ambiq_gpu_decode_codepoint(utf8, codepoint_size);
    const struct open_cfw_ambiq_gpu_font_range_view *range;

    if (codepoint == 0U) {
        return (const struct open_cfw_ambiq_gpu_glyph_view *)0;
    }
    range = font->ranges;
    while (range->glyphs != (const struct open_cfw_ambiq_gpu_glyph_view *)0) {
        if (codepoint >= range->first && codepoint <= range->last) {
            return &range->glyphs[codepoint - range->first];
        }
        ++range;
    }
    return (const struct open_cfw_ambiq_gpu_glyph_view *)0;
}
