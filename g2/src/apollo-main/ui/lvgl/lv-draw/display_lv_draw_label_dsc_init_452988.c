/* Apollo lv_obj_init_draw_label_dsc 0x452988..0x452a4b.
 * Control flow follows pinned LVGL src/core/lv_obj_draw.c.
 */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);
extern uint32_t audio_uart_lv_draw_task_opacity_452df0(void *, uint32_t, const void *);
extern uint32_t audio_uart_lv_draw_rgb_mix_452e22(void *, uint32_t,
    const void *, uint32_t);

static void put32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value; p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u); p[3] = (uint8_t)(value >> 24u);
}
static void put24(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value; p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u);
}

void audio_uart_lv_draw_label_dsc_init_452988(void *object, uint32_t part,
                                               void *descriptor) {
    uint8_t *d = (uint8_t *)descriptor;
    put32(d, (uint32_t)(uintptr_t)object);
    put32(d + 4u, part);
    uint8_t opacity = (uint8_t)audio_uart_lv_style_property_44bdea(
        object, part, 0x59u);
    d[0x50u] = opacity;
    if (opacity <= 2u) return;
    uint8_t layer_opacity = (uint8_t)audio_uart_lv_draw_task_opacity_452df0(
        object, part, descriptor);
    if (layer_opacity < 0xfdu) {
        opacity = (uint8_t)(((uint32_t)layer_opacity * opacity) >> 8u);
        d[0x50u] = opacity;
    }
    if (opacity <= 2u) return;
    const uint32_t color = audio_uart_lv_style_property_44bdea(
        object, part, 0x58u);
    put24(d + 0x24u, audio_uart_lv_draw_rgb_mix_452e22(
        object, part, descriptor, color));
    put32(d + 0x2cu, audio_uart_lv_style_property_44bdea(
        object, part, 0x5bu));
    put32(d + 0x28u, audio_uart_lv_style_property_44bdea(
        object, part, 0x5cu));
    d[0x53u] = (uint8_t)((d[0x53u] & 0xf8u) |
        (audio_uart_lv_style_property_44bdea(object, part, 0x5du) & 7u));
    put32(d + 0x20u, audio_uart_lv_style_property_44bdea(
        object, part, 0x5au));
    d[0x51u] = (uint8_t)audio_uart_lv_style_property_44bdea(
        object, part, 0x5eu);
}
