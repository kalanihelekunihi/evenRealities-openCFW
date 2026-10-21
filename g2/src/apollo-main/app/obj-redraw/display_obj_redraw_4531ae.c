/* Apollo Main LVGL object redraw, native 0x4531ae..0x4534be.
 * Flow follows pinned LVGL 9.3 lv_refr.c, with stock object/layer offsets. */
#include <stdint.h>

extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern void audio_uart_lv_obj_coords_43fc2a(void *, void *);
extern int32_t audio_uart_lv_obj_ext_draw_size_452dc8(void *);
extern void audio_uart_lv_area_expand_450b98(void *, int32_t, int32_t);
extern uint32_t audio_uart_lv_area_intersect_450bcc(void *, const void *,
                                                     const void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *, uint32_t);
extern uint32_t audio_uart_lv_child_count_44ddea(void *);
extern uint32_t audio_uart_lv_draw_style_metric_453160(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_style_metric_45316a(void *, uint32_t);
extern void audio_uart_lv_draw_object_4541b6(void *, void *);
extern void audio_uart_lv_mask_rect_dsc_init_48a984(void *);
extern void audio_uart_ambiq_image_options_init_488918(void *);
extern int32_t audio_uart_lv_area_width_451598(const void *);
extern int32_t audio_uart_lv_area_height_4515a4(const void *);
extern void *audio_uart_lv_draw_layer_create_48475e(void *, uint32_t,
                                                      const void *);
extern void audio_uart_lv_draw_mask_rect_48a98e(void *, const void *);
extern void audio_uart_lv_draw_layer_48895e(void *, const void *, const void *);

static void cp16(void *dst, const void *src)
{
    (void)audio_uart_display_area_copy_439c04(dst, src, 16u);
}

static void post_events(void *obj, void *layer)
{
    (void)audio_uart_lv_obj_event_451670(obj, 0x1fu, layer);
    (void)audio_uart_lv_obj_event_451670(obj, 0x20u, layer);
    (void)audio_uart_lv_obj_event_451670(obj, 0x21u, layer);
}

static void draw_children(void *layer, uint8_t *obj, uint32_t count)
{
    const uint8_t *const spec = (const uint8_t *)(uintptr_t)
        *(const uint32_t *)(const void *)(obj + 8u);
    const uint32_t table = *(const uint32_t *)(const void *)spec;
    for (uint32_t i = 0; i < count; ++i) {
        const uint32_t child = *(const uint32_t *)(uintptr_t)(table + i * 4u);
        audio_uart_lv_draw_object_4541b6(layer, (void *)(uintptr_t)child);
    }
}

void audio_uart_lv_obj_redraw_4531ae(void *layer_arg, void *object)
{
    uint8_t *const layer = (uint8_t *)layer_arg;
    uint8_t *const obj = (uint8_t *)object;
    int32_t original[4], expanded[4], main_clip[4], child_clip[4];
    cp16(original, layer + 0x18u);
    audio_uart_lv_obj_coords_43fc2a(object, expanded);
    const int32_t extra = audio_uart_lv_obj_ext_draw_size_452dc8(object);
    audio_uart_lv_area_expand_450b98(expanded, extra, extra);
    if (audio_uart_lv_area_intersect_450bcc(main_clip, original,
                                             expanded) == 0u)
        return;
    cp16(layer + 0x18u, main_clip);
    (void)audio_uart_lv_obj_event_451670(object, 0x1cu, layer);
    (void)audio_uart_lv_obj_event_451670(object, 0x1du, layer);
    (void)audio_uart_lv_obj_event_451670(object, 0x1eu, layer);

    const void *const obj_clip =
        audio_uart_lv_obj_has_flag_43e0e0(object, 0x100000u) != 0u ?
        (const void *)expanded : (const void *)(obj + 0x14u);
    if (audio_uart_lv_area_intersect_450bcc(child_clip, original,
                                             obj_clip) == 0u)
        goto restore;
    const uint32_t child_count = audio_uart_lv_child_count_44ddea(object);
    if (child_count == 0u) {
        cp16(layer + 0x18u, main_clip);
        post_events(object, layer);
        goto restore;
    }

    cp16(layer + 0x18u, child_clip);
    uint32_t clip_corner = audio_uart_lv_draw_style_metric_45316a(object, 0u);
    int32_t radius = 0;
    if ((uint8_t)clip_corner != 0u) {
        radius = (int32_t)audio_uart_lv_draw_style_metric_453160(object, 0u);
        if (radius == 0) clip_corner = 0u;
    }
    if ((uint8_t)clip_corner == 0u) {
        draw_children(layer, obj, child_count);
        cp16(layer + 0x18u, main_clip);
        post_events(object, layer);
        goto restore;
    }

    uint8_t mask[0x34u];
    uint8_t image[0x6cu];
    audio_uart_lv_mask_rect_dsc_init_48a984(mask);
    *(int32_t *)(void *)(mask + 0x2cu) = radius;
    cp16(mask + 0x1cu, obj + 0x14u);
    audio_uart_ambiq_image_options_init_488918(image);
    const int32_t width = audio_uart_lv_area_width_451598(obj + 0x14u);
    const int32_t height = audio_uart_lv_area_height_4515a4(obj + 0x14u);
    const int32_t short_side = width < height ?
        audio_uart_lv_area_width_451598(obj + 0x14u) :
        audio_uart_lv_area_height_4515a4(obj + 0x14u);
    const int32_t half = short_side >> 1;
    const int32_t rout = radius < half ? radius : half;

    int32_t bottom[4];
    cp16(bottom, obj + 0x14u);
    bottom[1] = bottom[3] - rout + 1;
    if (audio_uart_lv_area_intersect_450bcc(bottom, bottom, original) != 0u) {
        uint8_t *const child = (uint8_t *)audio_uart_lv_draw_layer_create_48475e(
            layer, 0x10u, bottom);
        draw_children(child, obj, child_count);
        post_events(object, child);
        audio_uart_lv_draw_mask_rect_48a98e(child, mask);
        *(uint32_t *)(void *)(image + 0x1cu) = (uint32_t)(uintptr_t)child;
        audio_uart_lv_draw_layer_48895e(layer, image, bottom);
    }

    int32_t top[4];
    cp16(top, obj + 0x14u);
    top[3] = top[1] + rout - 1;
    if (audio_uart_lv_area_intersect_450bcc(top, top, original) != 0u) {
        uint8_t *const child = (uint8_t *)audio_uart_lv_draw_layer_create_48475e(
            layer, 0x10u, top);
        draw_children(child, obj, child_count);
        post_events(object, child);
        audio_uart_lv_draw_mask_rect_48a98e(child, mask);
        *(uint32_t *)(void *)(image + 0x1cu) = (uint32_t)(uintptr_t)child;
        audio_uart_lv_draw_layer_48895e(layer, image, top);
    }

    int32_t middle[4];
    cp16(middle, obj + 0x14u);
    middle[1] += rout;
    middle[3] -= rout;
    if (audio_uart_lv_area_intersect_450bcc(middle, middle, original) != 0u) {
        cp16(layer + 0x18u, middle);
        draw_children(layer, obj, child_count);
        post_events(object, layer);
    }
restore:
    cp16(layer + 0x18u, original);
}
