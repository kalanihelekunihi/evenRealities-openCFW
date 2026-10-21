/* Apollo Main LVGL v9.3 draw-buffer initialization 0x48aef8..0x48aff9. */
#include <stdint.h>

extern void audio_uart_lv_draw_memzero_48aa54(void *, uint32_t);
extern uint32_t audio_uart_font_bitmap_stride(uint32_t, uint8_t);
extern void *audio_uart_lv_draw_align_48ab04(void *, uint32_t);
extern uint8_t audio_uart_display_lv_state[];
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
static const char function[] = "lv_draw_buf_init";
static const char insufficient[] =
    "Data size too small, required: %d, provided: %d";
static const char unaligned[] = "Data is not aligned, ignored";

uint32_t audio_uart_display_platform_bind(void *draw_buffer, uint32_t width,
                                          uint32_t height, uint32_t color_format,
                                          uint32_t stride, void *data,
                                          uint32_t data_size)
{
    if (draw_buffer == 0) {
        audio_uart_lvgl_log(3u, source, 0x11eu, function,
                            "Asserted at expression: %s (%s)",
                            "draw_buf != NULL", "NULL pointer");
        __builtin_trap();
    }
    uint8_t *const out = (uint8_t *)draw_buffer;
    audio_uart_lv_draw_memzero_48aa54(out, 28u);
    const uint8_t format = (uint8_t)color_format;
    if (stride == 0u) stride = audio_uart_font_bitmap_stride(width, format);
    const uint32_t required = height * stride;
    if (data_size < required) {
        audio_uart_lvgl_log(2u, source, 0x125u, function,
                            insufficient, required, data_size);
        return 0u;
    }
    *(uint32_t *)(void *)(out + 4u) =
        (width & 0xffffu) | ((height & 0xffffu) << 16u);
    out[0] = 0x19u;
    out[1] = format;
    *(uint16_t *)(void *)(out + 8u) = (uint16_t)stride;
    *(void **)(void *)(out + 16u) = data;
    *(void **)(void *)(out + 20u) = data;
    *(uint32_t *)(void *)(out + 24u) =
        (uint32_t)(uintptr_t)(audio_uart_display_lv_state + 0xc8u);
    *(uint32_t *)(void *)(out + 12u) = data_size;
    if (audio_uart_lv_draw_align_48ab04(data, format) != data)
        audio_uart_lvgl_log(2u, source, 0x136u, function, unaligned);
    return 1u;
}
