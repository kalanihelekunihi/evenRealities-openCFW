/* SPDX-License-Identifier: MIT */
/*
 * Bounded LVGL fmt_txt bitmap provider for the isolated G2/Ambiq link audit.
 * The unpacking and RLE state machine follow authenticated LVGL source.  RLE
 * state and line storage are local so this provider does not claim ownership
 * of LVGL's mutable global or heap.  Production routing remains a separate
 * integration decision.
 */
#include "lvgl_ambiq_lvgl_font_fmt_provider.h"
#include "src/draw/lv_draw_buf_private.h"

#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

enum {
    OPENCFW_RLE_SINGLE = 0,
    OPENCFW_RLE_REPEATED,
    OPENCFW_RLE_COUNTER,
};

typedef struct {
    const uint8_t * input;
    uint32_t read_bit;
    uint8_t previous;
    uint8_t count;
    uint8_t bits_per_pixel;
    uint8_t state;
} open_cfw_rle_t;

static const uint8_t opacity2[4] = {0U, 85U, 170U, 255U};
static const uint8_t opacity3[8] = {0U, 36U, 73U, 109U, 146U, 182U, 218U, 255U};
static const uint8_t opacity4[16] = {
    0U, 17U, 34U, 51U, 68U, 85U, 102U, 119U,
    136U, 153U, 170U, 187U, 204U, 221U, 238U, 255U,
};

static uint8_t open_cfw_get_bits(const uint8_t * input, uint32_t bit_pos,
                                 uint8_t length)
{
    uint16_t mask = (uint16_t)(((uint16_t)1U << length) - 1U);
    uint32_t byte_pos = bit_pos >> 3;
    uint8_t byte_bit = (uint8_t)(bit_pos & 7U);

    if((uint8_t)(byte_bit + length) >= 8U) {
        uint16_t value = (uint16_t)(((uint16_t)input[byte_pos] << 8) |
                                    input[byte_pos + 1U]);
        return (uint8_t)((value >> (16U - byte_bit - length)) & mask);
    }
    return (uint8_t)((input[byte_pos] >> (8U - byte_bit - length)) & mask);
}

static uint8_t open_cfw_rle_next(open_cfw_rle_t * rle)
{
    uint8_t value;
    uint8_t result = 0U;

    if(rle->state == OPENCFW_RLE_SINGLE) {
        result = open_cfw_get_bits(rle->input, rle->read_bit,
                                   rle->bits_per_pixel);
        if(rle->read_bit != 0U && rle->previous == result) {
            rle->count = 0U;
            rle->state = OPENCFW_RLE_REPEATED;
        }
        rle->previous = result;
        rle->read_bit += rle->bits_per_pixel;
    }
    else if(rle->state == OPENCFW_RLE_REPEATED) {
        value = open_cfw_get_bits(rle->input, rle->read_bit, 1U);
        rle->count++;
        rle->read_bit++;
        if(value != 0U) {
            result = rle->previous;
            if(rle->count == 11U) {
                rle->count = open_cfw_get_bits(rle->input, rle->read_bit, 6U);
                rle->read_bit += 6U;
                if(rle->count != 0U) {
                    rle->state = OPENCFW_RLE_COUNTER;
                }
                else {
                    result = open_cfw_get_bits(rle->input, rle->read_bit,
                                               rle->bits_per_pixel);
                    rle->previous = result;
                    rle->read_bit += rle->bits_per_pixel;
                    rle->state = OPENCFW_RLE_SINGLE;
                }
            }
        }
        else {
            result = open_cfw_get_bits(rle->input, rle->read_bit,
                                       rle->bits_per_pixel);
            rle->previous = result;
            rle->read_bit += rle->bits_per_pixel;
            rle->state = OPENCFW_RLE_SINGLE;
        }
    }
    else {
        result = rle->previous;
        rle->count--;
        if(rle->count == 0U) {
            result = open_cfw_get_bits(rle->input, rle->read_bit,
                                       rle->bits_per_pixel);
            rle->previous = result;
            rle->read_bit += rle->bits_per_pixel;
            rle->state = OPENCFW_RLE_SINGLE;
        }
    }
    return result;
}

static bool open_cfw_output_is_bounded(const lv_draw_buf_t * draw_buf,
                                       uint32_t width, uint32_t height,
                                       uint32_t * stride_out)
{
    uintptr_t allocation;
    uintptr_t output;
    uint32_t offset;
    uint32_t stride;
    uint32_t required;

    if(draw_buf == NULL || draw_buf->data == NULL ||
       draw_buf->unaligned_data == NULL || stride_out == NULL) return false;
    if(width == 0U || height == 0U || draw_buf->header.w < width ||
       draw_buf->header.h < height) return false;

    stride = draw_buf->header.stride;
    if(stride < width || height > UINT32_MAX / stride) return false;
    required = stride * height;

    allocation = (uintptr_t)draw_buf->unaligned_data;
    output = (uintptr_t)draw_buf->data;
    if(output < allocation || output - allocation > UINT32_MAX) return false;
    offset = (uint32_t)(output - allocation);
    if(offset > draw_buf->data_size || required > draw_buf->data_size - offset) return false;

    *stride_out = stride;
    return true;
}

static uint8_t open_cfw_expand_plain(uint8_t packed, uint8_t bpp)
{
    if(bpp == 1U) return packed != 0U ? 255U : 0U;
    if(bpp == 2U) return opacity2[packed];
    if(bpp == 4U) return opacity4[packed];
    return packed;
}

static void open_cfw_flush(const lv_draw_buf_t * draw_buf)
{
    if(draw_buf->handlers != NULL && draw_buf->handlers->flush_cache_cb != NULL) {
        draw_buf->handlers->flush_cache_cb(draw_buf, NULL);
    }
}

static bool open_cfw_decode_plain(const uint8_t * input, uint8_t * output,
                                  uint32_t width, uint32_t height,
                                  uint32_t stride, uint8_t bpp,
                                  bool row_aligned)
{
    uint32_t bit = 0U;
    uint32_t y;

    if(bpp != 1U && bpp != 2U && bpp != 4U && bpp != 8U) return false;
    for(y = 0U; y < height; y++) {
        uint32_t x;
        if(row_aligned && (bit & 7U) != 0U) bit = (bit + 7U) & ~7U;
        for(x = 0U; x < width; x++) {
            uint8_t value = open_cfw_get_bits(input, bit, bpp);
            output[x] = open_cfw_expand_plain(value, bpp);
            bit += bpp;
        }
        output += stride;
    }
    return true;
}

static bool open_cfw_decode_compressed(const uint8_t * input, uint8_t * output,
                                       uint32_t width, uint32_t height,
                                       uint32_t stride, uint8_t bpp,
                                       bool prefilter)
{
    const uint8_t * table;
    open_cfw_rle_t rle = {
        .input = input,
        .read_bit = 0U,
        .previous = 0U,
        .count = 0U,
        .bits_per_pixel = bpp,
        .state = OPENCFW_RLE_SINGLE,
    };
    uint32_t x;
    uint32_t y;

    if(bpp == 2U) table = opacity2;
    else if(bpp == 3U) table = opacity3;
    else if(bpp == 4U) table = opacity4;
    else return false;

    for(y = 0U; y < height; y++) {
        for(x = 0U; x < width; x++) {
            uint8_t raw = open_cfw_rle_next(&rle);
            if(prefilter && y != 0U) {
                uint8_t previous_opacity = (output - stride)[x];
                uint8_t previous_raw = 0U;
                uint8_t candidate;
                uint8_t table_size = (uint8_t)(1U << bpp);
                for(candidate = 0U; candidate < table_size; candidate++) {
                    if(table[candidate] == previous_opacity) {
                        previous_raw = candidate;
                        break;
                    }
                }
                raw ^= previous_raw;
            }
            output[x] = table[raw];
        }
        output += stride;
    }
    return true;
}

const void * lv_font_get_bitmap_fmt_txt(lv_font_glyph_dsc_t * glyph,
                                        lv_draw_buf_t * draw_buf)
{
    const lv_font_t * font;
    const lv_font_fmt_txt_dsc_t * font_dsc;
    const lv_font_fmt_txt_glyph_dsc_t * glyph_dsc;
    const uint8_t * input;
    uint32_t stride;
    uint32_t glyph_id;
    bool decoded;

    if(glyph == NULL || draw_buf == NULL || glyph->resolved_font == NULL) return NULL;
    font = glyph->resolved_font;
    if(font->dsc == NULL) return NULL;
    font_dsc = (const lv_font_fmt_txt_dsc_t *)font->dsc;
    glyph_id = glyph->gid.index;
    if(glyph_id == 0U || font_dsc->glyph_dsc == NULL ||
       font_dsc->glyph_bitmap == NULL) return NULL;

    glyph_dsc = &font_dsc->glyph_dsc[glyph_id];
    input = &font_dsc->glyph_bitmap[glyph_dsc->bitmap_index];
    if(glyph->req_raw_bitmap) return input;
    if(!open_cfw_output_is_bounded(draw_buf, glyph_dsc->box_w,
                                   glyph_dsc->box_h, &stride)) return NULL;

    if(font_dsc->bitmap_format == LV_FONT_FMT_TXT_PLAIN ||
       font_dsc->bitmap_format == LV_FONT_FMT_PLAIN_ALIGNED) {
        decoded = open_cfw_decode_plain(
            input, draw_buf->data, glyph_dsc->box_w, glyph_dsc->box_h, stride,
            (uint8_t)font_dsc->bpp,
            font_dsc->bitmap_format == LV_FONT_FMT_PLAIN_ALIGNED);
    }
    else if(font_dsc->bitmap_format == LV_FONT_FMT_TXT_COMPRESSED ||
            font_dsc->bitmap_format == LV_FONT_FMT_TXT_COMPRESSED_NO_PREFILTER) {
        decoded = open_cfw_decode_compressed(
            input, draw_buf->data, glyph_dsc->box_w, glyph_dsc->box_h, stride,
            (uint8_t)font_dsc->bpp,
            font_dsc->bitmap_format == LV_FONT_FMT_TXT_COMPRESSED);
    }
    else {
        return NULL;
    }

    if(!decoded) return NULL;
    open_cfw_flush(draw_buf);
    return draw_buf;
}
