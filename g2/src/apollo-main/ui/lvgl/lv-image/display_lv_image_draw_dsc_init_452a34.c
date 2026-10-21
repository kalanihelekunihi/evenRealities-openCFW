/* Stock lv_obj_init_draw_image_dsc, 0x452a34..0x452b0d. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_image_opa_4524a4(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_task_opacity_452df0(void *, uint32_t,
                                                        const void *);
extern int32_t audio_uart_lv_area_width_451598(const void *);
extern int32_t audio_uart_lv_area_height_4515a4(const void *);
extern uint32_t audio_uart_lv_style_image_recolor_4524b0(void *, uint32_t);
extern uint32_t audio_uart_lv_style_image_recolor_opa_4524d0(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_color_variant_452e68(void *, uint32_t,
                                                         const void *, uint32_t,
                                                         uint32_t);
extern uint32_t audio_uart_page_441068(uint32_t, uint32_t, uint32_t);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);
extern uint32_t audio_uart_lv_style_image_blend_45260a(void *, uint32_t);

static void put(uint8_t *bytes, uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(bytes + offset) = value;
}

uint32_t audio_uart_lv_obj_init_draw_image_452a34(void *object, uint32_t part,
                                                    void *descriptor,
                                                    uint32_t initial_result) {
    uint8_t *d = (uint8_t *)descriptor;
    put(d, 0u, (uint32_t)(uintptr_t)object);
    put(d, 4u, part);
    uint8_t opacity =
        (uint8_t)audio_uart_lv_style_image_opa_4524a4(object, part);
    d[0x50u] = opacity;
    if (opacity <= 2u)
        return initial_result;
    const uint8_t layer_opacity =
        (uint8_t)audio_uart_lv_draw_task_opacity_452df0(object, part, d);
    if (layer_opacity < 0xfdu) {
        opacity = (uint8_t)(((uint32_t)layer_opacity * opacity) >> 8u);
        d[0x50u] = opacity;
    }
    if (d[0x50u] <= 2u)
        return initial_result;
    put(d, 0x30u, 0u);
    put(d, 0x34u, 0x100u);
    put(d, 0x38u, 0x100u);
    const uint8_t *obj = (const uint8_t *)object;
    put(d, 0x44u,
        (uint32_t)(audio_uart_lv_area_width_451598(obj + 0x14u) / 2));
    put(d, 0x48u,
        (uint32_t)(audio_uart_lv_area_height_4515a4(obj + 0x14u) / 2));
    const uint32_t color =
        audio_uart_lv_style_image_recolor_4524b0(object, part);
    const uint32_t recolor_opacity = (uint8_t)
        audio_uart_lv_style_image_recolor_opa_4524d0(object, part);
    const uint32_t variant = audio_uart_lv_draw_color_variant_452e68(
        object, part, d, color, recolor_opacity);
    d[0x4fu] = (uint8_t)(variant >> 24u);
    const uint32_t rgb = audio_uart_page_441068(
        (variant >> 16u) & 0xffu, (variant >> 8u) & 0xffu,
        variant & 0xffu);
    (void)audio_queue_copy_bytes(d + 0x4cu, &rgb, 3u);
    if (part != 0u)
        d[0x51u] = (uint8_t)((d[0x51u] & ~7u) |
            (audio_uart_lv_style_image_blend_45260a(object, part) & 7u));
    return rgb;
}
