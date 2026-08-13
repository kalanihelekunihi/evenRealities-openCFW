/* SPDX-License-Identifier: GPL-3.0-only */

#include "../../components/shared/lvgl/runtime_ambiq_gpu_patch_get_glyph_candidate.h"

static struct open_cfw_ambiq_gpu_glyph_view first_glyphs[3];
static struct open_cfw_ambiq_gpu_glyph_view two_byte_glyph;
static struct open_cfw_ambiq_gpu_glyph_view three_byte_glyph;
static struct open_cfw_ambiq_gpu_glyph_view four_byte_glyphs[2];
static const struct open_cfw_ambiq_gpu_font_range_view ranges[] = {
    {0x41U, 0x43U, first_glyphs},
    {0xA2U, 0xA2U, &two_byte_glyph},
    {0x20ACU, 0x20ACU, &three_byte_glyph},
    {0x1F600U, 0x1F601U, four_byte_glyphs},
    {0U, 0U, 0},
};
static const struct open_cfw_ambiq_gpu_font_view font = {1U, ranges};
static uint32_t forced_size;

static uint32_t size_port(const uint8_t *utf8)
{
    uint8_t value = utf8[0];
    if (forced_size != 0xFFFFFFFFU) {
        return forced_size;
    }
    if ((value & 0x80U) == 0U) return 1U;
    if ((value & 0xE0U) == 0xC0U) return 2U;
    if ((value & 0xF0U) == 0xE0U) return 3U;
    if ((value & 0xF8U) == 0xF0U) return 4U;
    return 0U;
}

void open_cfw_test_ambiq_glyph_reset(void)
{
    uint32_t index;
    for (index = 0; index < 3U; ++index) first_glyphs[index].data_offset = 100U + index;
    two_byte_glyph.data_offset = 200U;
    three_byte_glyph.data_offset = 300U;
    for (index = 0; index < 2U; ++index) four_byte_glyphs[index].data_offset = 400U + index;
    forced_size = 0xFFFFFFFFU;
}

void open_cfw_test_ambiq_glyph_force_size(uint32_t size) { forced_size = size; }

uint32_t open_cfw_test_ambiq_glyph_lookup(const char *character)
{
    const struct open_cfw_ambiq_gpu_glyph_view *glyph =
        open_cfw_ambiq_gpu_get_glyph_candidate(&font, character, size_port);
    return glyph == 0 ? 0U : glyph->data_offset;
}
