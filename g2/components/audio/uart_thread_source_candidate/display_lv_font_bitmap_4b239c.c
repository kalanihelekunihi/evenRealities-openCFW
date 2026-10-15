/* Apollo Main LV font bitmap callback, native 0x4b239c..0x4b268f. */
#include <stdint.h>

extern uint32_t audio_uart_font_bitmap_stride(uint32_t width, uint8_t format);
extern void audio_uart_lvgl_log(uint32_t level, const char *file, uint32_t line,
                               const char *function, const char *message);

static uint16_t get16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8u));
}
static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

static const uint8_t opacity2[4] = {0x00, 0x55, 0xaa, 0xff};
static const uint8_t opacity4[16] = {
    0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
    0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff
};

void *audio_uart_lv_font_glyph_bitmap_4b239c(const void *glyph_descriptor,
                                               void *draw_buffer) {
    const uint8_t *glyph = (const uint8_t *)glyph_descriptor;
    const uint8_t *font = (const uint8_t *)(uintptr_t)get32(glyph);
    const uint8_t *state = (const uint8_t *)(uintptr_t)get32(font + 0x18u);
    uint8_t *buffer = (uint8_t *)draw_buffer;
    uint8_t *dst = (uint8_t *)(uintptr_t)get32(buffer + 0x10u);
    uint32_t glyph_id = get32(glyph + 0x18u);
    if (glyph_id == 0u) return 0;
    const uint8_t *entry = (const uint8_t *)(uintptr_t)get32(state + 4u) +
                           glyph_id * 16u;
    const uint8_t *src = (const uint8_t *)(uintptr_t)get32(state) + get32(entry);
    if ((glyph[0x14u] & 1u) != 0u) return (void *)src;
    uint32_t width = get16(entry + 8u);
    uint32_t height = get16(entry + 10u);
    if (width * height == 0u) return 0;
    uint16_t flags = get16(state + 0x12u);
    uint32_t packing = flags >> 14u;
    if (packing != 0u && packing != 3u) {
        audio_uart_lvgl_log(2u, (const char *)(uintptr_t)0x006e0740u,
                           0xc1u, (const char *)(uintptr_t)0x0076cb6cu,
                           (const char *)(uintptr_t)0x006edd88u);
        return 0;
    }
    uint32_t stride = audio_uart_font_bitmap_stride(width, 14u);
    uint32_t bpp = (flags >> 9u) & 0x0fu;
    uint32_t position = 0u;
    for (uint32_t y = 0u; y < height; ++y) {
        if (bpp == 1u || bpp == 2u || bpp == 4u) {
            uint32_t pixels_per_byte = 8u / bpp;
            for (uint32_t x = 0u; x < width; ++x) {
                uint32_t slot = position & (pixels_per_byte - 1u);
                uint32_t shift = 8u - bpp * (slot + 1u);
                uint32_t sample = ((uint32_t)*src >> shift) & ((1u << bpp) - 1u);
                dst[x] = bpp == 1u ? (sample ? 0xffu : 0u) :
                         bpp == 2u ? opacity2[sample] : opacity4[sample];
                if (slot == pixels_per_byte - 1u) ++src;
                ++position;
            }
            if (packing == 3u && position != 0u) {
                position = 0u;
                ++src;
            }
        } else if (bpp == 8u) {
            for (uint32_t x = 0u; x < width; ++x) {
                dst[x] = *src++;
                ++position;
            }
        }
        dst += stride;
    }
    return buffer;
}
