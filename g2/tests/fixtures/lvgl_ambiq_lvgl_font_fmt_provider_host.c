/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_font_fmt_provider.h"
#include "src/draw/lv_draw_buf_private.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static unsigned flush_count;

static void flush_cb(const lv_draw_buf_t * draw_buf, const lv_area_t * area)
{
    assert(draw_buf != NULL);
    assert(area == NULL);
    flush_count++;
}

static lv_draw_buf_handlers_t handlers = {
    .flush_cache_cb = flush_cb,
};

typedef struct {
    lv_font_fmt_txt_glyph_dsc_t glyphs[2];
    lv_font_fmt_txt_dsc_t font_dsc;
    lv_font_t font;
    lv_font_glyph_dsc_t glyph;
    lv_draw_buf_t draw_buf;
    uint8_t allocation[96];
} fixture_t;

static void fixture_init(fixture_t * fixture, const uint8_t * bitmap,
                         uint8_t bpp, lv_font_fmt_txt_bitmap_format_t format,
                         uint8_t width, uint8_t height, uint32_t stride)
{
    memset(fixture, 0, sizeof(*fixture));
    fixture->glyphs[1].box_w = width;
    fixture->glyphs[1].box_h = height;
    fixture->font_dsc.glyph_bitmap = bitmap;
    fixture->font_dsc.glyph_dsc = fixture->glyphs;
    fixture->font_dsc.bpp = bpp;
    fixture->font_dsc.bitmap_format = format;
    fixture->font.dsc = &fixture->font_dsc;
    fixture->glyph.resolved_font = &fixture->font;
    fixture->glyph.gid.index = 1U;
    fixture->draw_buf.header.cf = LV_COLOR_FORMAT_A8;
    fixture->draw_buf.header.w = width;
    fixture->draw_buf.header.h = height;
    fixture->draw_buf.header.stride = stride;
    fixture->draw_buf.data_size = sizeof(fixture->allocation);
    fixture->draw_buf.unaligned_data = fixture->allocation;
    fixture->draw_buf.data = fixture->allocation + 3U;
    fixture->draw_buf.handlers = &handlers;
    memset(fixture->draw_buf.data, 0xCC, sizeof(fixture->allocation) - 3U);
}

static void expect_row(const fixture_t * fixture, uint32_t row,
                       const uint8_t * expected, uint32_t width)
{
    const uint8_t * actual = fixture->draw_buf.data +
                             row * fixture->draw_buf.header.stride;
    assert(memcmp(actual, expected, width) == 0);
    if(fixture->draw_buf.header.stride > width) assert(actual[width] == 0xCC);
}

static void test_plain_formats(void)
{
    fixture_t fixture;
    static const uint8_t bits1[] = {0xAC, 0x00};
    static const uint8_t aligned1[] = {0xA0, 0x60, 0x00};
    static const uint8_t bits2[] = {0x1B, 0x00};
    static const uint8_t bits4[] = {0x0F, 0x00};
    static const uint8_t bits8[] = {7U, 250U, 0U};
    static const uint8_t row101[] = {255U, 0U, 255U};
    static const uint8_t row011[] = {0U, 255U, 255U};
    static const uint8_t row2[] = {0U, 85U, 170U, 255U};
    static const uint8_t row4[] = {0U, 255U};
    static const uint8_t row8[] = {7U, 250U};

    flush_count = 0U;
    fixture_init(&fixture, bits1, 1U, LV_FONT_FMT_TXT_PLAIN, 3U, 2U, 5U);
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, &fixture.draw_buf) ==
           &fixture.draw_buf);
    expect_row(&fixture, 0U, row101, 3U);
    expect_row(&fixture, 1U, row011, 3U);

    fixture_init(&fixture, aligned1, 1U, LV_FONT_FMT_PLAIN_ALIGNED, 3U, 2U, 5U);
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, &fixture.draw_buf) ==
           &fixture.draw_buf);
    expect_row(&fixture, 0U, row101, 3U);
    expect_row(&fixture, 1U, row011, 3U);

    fixture_init(&fixture, bits2, 2U, LV_FONT_FMT_TXT_PLAIN, 4U, 1U, 6U);
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, &fixture.draw_buf));
    expect_row(&fixture, 0U, row2, 4U);

    fixture_init(&fixture, bits4, 4U, LV_FONT_FMT_TXT_PLAIN, 2U, 1U, 4U);
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, &fixture.draw_buf));
    expect_row(&fixture, 0U, row4, 2U);

    fixture_init(&fixture, bits8, 8U, LV_FONT_FMT_TXT_PLAIN, 2U, 1U, 4U);
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, &fixture.draw_buf));
    expect_row(&fixture, 0U, row8, 2U);
    assert(flush_count == 5U);
}

static void test_compressed_formats(void)
{
    fixture_t fixture;
    static const uint8_t encoded[] = {0x1B, 0x77, 0x00};
    static const uint8_t encoded_counter[] = {0x0F, 0xFE, 0x1A, 0x00};
    static const uint8_t first[] = {0U, 85U, 170U, 255U};
    static const uint8_t second_prefilter[] = {85U, 170U, 255U, 0U};
    static const uint8_t second_raw[] = {85U, 255U, 85U, 255U};
    static const uint8_t counter_result[] = {
        0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U,
        0U, 0U, 0U, 0U, 0U, 0U, 0U, 85U,
    };

    flush_count = 0U;
    fixture_init(&fixture, encoded, 2U, LV_FONT_FMT_TXT_COMPRESSED, 4U, 2U, 6U);
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, &fixture.draw_buf));
    expect_row(&fixture, 0U, first, 4U);
    expect_row(&fixture, 1U, second_prefilter, 4U);

    fixture_init(&fixture, encoded, 2U, LV_FONT_FMT_TXT_COMPRESSED_NO_PREFILTER,
                 4U, 2U, 6U);
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, &fixture.draw_buf));
    expect_row(&fixture, 0U, first, 4U);
    expect_row(&fixture, 1U, second_raw, 4U);

    fixture_init(&fixture, encoded_counter, 2U,
                 LV_FONT_FMT_TXT_COMPRESSED_NO_PREFILTER, 16U, 1U, 18U);
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, &fixture.draw_buf));
    expect_row(&fixture, 0U, counter_result, 16U);
    assert(flush_count == 3U);
}

static void test_fail_closed_and_raw(void)
{
    fixture_t fixture;
    static const uint8_t bitmap[] = {0xA0, 0x00};
    uint8_t snapshot[96];

    fixture_init(&fixture, bitmap, 1U, LV_FONT_FMT_TXT_PLAIN, 3U, 1U, 4U);
    fixture.glyph.req_raw_bitmap = 1U;
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, &fixture.draw_buf) == bitmap);
    assert(flush_count == 3U);
    fixture.glyph.req_raw_bitmap = 0U;

    memcpy(snapshot, fixture.allocation, sizeof(snapshot));
    assert(lv_font_get_bitmap_fmt_txt(NULL, &fixture.draw_buf) == NULL);
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, NULL) == NULL);
    fixture.glyph.gid.index = 0U;
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, &fixture.draw_buf) == NULL);
    fixture.glyph.gid.index = 1U;
    fixture.draw_buf.header.stride = 2U;
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, &fixture.draw_buf) == NULL);
    fixture.draw_buf.header.stride = 4U;
    fixture.draw_buf.data_size = 3U;
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, &fixture.draw_buf) == NULL);
    fixture.draw_buf.data_size = sizeof(fixture.allocation);
    fixture.font_dsc.bpp = 3U;
    assert(lv_font_get_bitmap_fmt_txt(&fixture.glyph, &fixture.draw_buf) == NULL);
    assert(memcmp(snapshot, fixture.allocation, sizeof(snapshot)) == 0);
    assert(flush_count == 3U);
}

int main(void)
{
    test_plain_formats();
    test_compressed_formats();
    test_fail_closed_and_raw();
    return 0;
}
