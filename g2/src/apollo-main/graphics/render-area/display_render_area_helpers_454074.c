/* Apollo Main LVGL layer draw-area selection and cover event gate,
 * stock 0x454074..0x454152 and 0x45417c..0x4541b6. */
#include <stdint.h>

extern uint32_t audio_uart_lv_obj_ext_draw_size_452dc8(void *);
extern void audio_uart_lv_obj_coords_43fc2a(void *, void *);
extern void audio_uart_lv_area_expand_450b98(void *, int32_t, int32_t);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern void audio_uart_lv_obj_adjust_area_440494(void *, void *, uint32_t);
extern uint32_t audio_uart_lv_area_intersect_450bcc(void *, const void *,
                                                    const void *);
extern uint32_t audio_uart_lv_area_overlap_450f00(const void *, const void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_refr.c";

typedef struct {
    uint8_t result;
    uint8_t padding[3];
    const void *area;
} cover_event_t;

uint32_t audio_uart_lv_render_area_select_454074(void *layer, void *object,
                                                  uint32_t type, void *out,
                                                  void *object_area)
{
    const uint32_t extra = audio_uart_lv_obj_ext_draw_size_452dc8(object);
    audio_uart_lv_obj_coords_43fc2a(object, object_area);
    audio_uart_lv_area_expand_450b98(object_area, (int32_t)extra,
                                      (int32_t)extra);
    if ((uint8_t)type == 2u) {
        int32_t preliminary[4];
        int32_t clipped[4];
        (void)audio_uart_display_area_copy_439c04(preliminary,
                                                    object_area, 16u);
        audio_uart_lv_obj_adjust_area_440494(object, preliminary, 0u);
        if (audio_uart_lv_area_intersect_450bcc(
                clipped, (const uint8_t *)layer + 0x18u,
                preliminary) == 0u)
            return 0u;
        int32_t adjusted[4];
        (void)audio_uart_display_area_copy_439c04(adjusted, clipped, 16u);
        audio_uart_lv_obj_adjust_area_440494(object, adjusted, 2u);
        if (audio_uart_lv_area_intersect_450bcc(
                adjusted, adjusted, object_area) == 0u)
            return 0u;
        (void)audio_uart_display_area_copy_439c04(out, adjusted, 16u);
        audio_uart_lv_area_expand_450b98(out, 5, 5);
        return 1u;
    }
    if ((uint8_t)type == 1u) {
        int32_t clipped[4];
        if (audio_uart_lv_area_intersect_450bcc(
                clipped, (const uint8_t *)layer + 0x18u,
                object_area) == 0u)
            return 0u;
        (void)audio_uart_display_area_copy_439c04(out, clipped, 16u);
        return 1u;
    }
    audio_uart_lvgl_log(2u, source, 0x3c1u, "layer_get_area",
                        "Unhandled layer type");
    return 0u;
}

uint32_t audio_uart_lv_render_cover_event_45417c(void *object,
                                                   const void *area)
{
    if (audio_uart_lv_area_overlap_450f00(area,
            (const uint8_t *)object + 0x14u) == 0u)
        return 1u;
    cover_event_t event = {0u, {0u, 0u, 0u}, area};
    (void)audio_uart_lv_obj_event_451670(object, 0x1au, &event);
    return event.result != 0u;
}
