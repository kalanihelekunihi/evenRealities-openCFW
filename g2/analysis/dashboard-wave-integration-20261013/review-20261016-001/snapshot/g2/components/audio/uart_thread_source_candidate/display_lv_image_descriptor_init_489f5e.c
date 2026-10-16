/* Apollo LV palette and 100-byte image descriptor defaults. */
#include <stdint.h>

extern const unsigned char audio_uart_display_page_style[];
extern void audio_uart_lvgl_log(uint32_t level, const char *source, uint32_t line,
                                const char *function, ...);

/* Authenticated Main ROM 0x716330..0x716368, nineteen RGB triples. */
const uint8_t audio_uart_lv_palette_table_716330[57] = {
    0x36,0x43,0xf4, 0x63,0x1e,0xe9, 0xb0,0x27,0x9c, 0xb7,0x3a,0x67,
    0xb5,0x51,0x3f, 0xf3,0x96,0x21, 0xf4,0xa9,0x03, 0xd4,0xbc,0x00,
    0x88,0x96,0x00, 0x50,0xaf,0x4c, 0x4a,0xc3,0x8b, 0x39,0xdc,0xcd,
    0x3b,0xeb,0xff, 0x07,0xc1,0xff, 0x00,0x98,0xff, 0x22,0x57,0xff,
    0x48,0x55,0x79, 0x8b,0x7d,0x60, 0x9e,0x9e,0x9e
};

static const char palette_source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_palette.c";
static const char palette_function[] = "lv_palette_main";
static const char palette_error[] = "Invalid palette: %d";

uint32_t audio_uart_page_488290(uint32_t palette) {
    uint32_t index = (uint8_t)palette;
    if (index >= 19u) {
        audio_uart_lvgl_log(2u, palette_source, 0x2eu, palette_function,
                            palette_error, index);
        return 0u;
    }
    const uint8_t *rgb = audio_uart_lv_palette_table_716330 + index * 3u;
    return (uint32_t)rgb[0] | ((uint32_t)rgb[1] << 8u) | ((uint32_t)rgb[2] << 16u);
}

void audio_uart_lv_image_descriptor_init_489f5e(void *descriptor) {
    uint8_t *p = (uint8_t *)descriptor;
    for (unsigned i = 0; i < 100u; ++i) p[i] = 0u;
    p[0x50u] = 0xffu;
    *(uint32_t *)(void *)(p + 0x4cu) = 0xffffffffu;
    *(uint32_t *)(void *)(p + 0x20u) =
        (uint32_t)(uintptr_t)audio_uart_display_page_style;
    *(uint32_t *)(void *)(p + 0x3cu) = 0xffffu;
    *(uint32_t *)(void *)(p + 0x40u) = 0xffffu;
    uint32_t color = audio_uart_page_488290(5u);
    for (unsigned i = 0; i < 3u; ++i) p[0x47u + i] = (uint8_t)(color >> (i * 8u));
    p[0x52u] = 0u;
    *(uint32_t *)(void *)(p + 0x14u) = 100u;
}
