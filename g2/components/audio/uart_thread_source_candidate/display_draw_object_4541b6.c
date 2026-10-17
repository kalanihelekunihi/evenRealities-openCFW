/* Apollo Main LVGL object refresh, native 0x4541b6..0x4544ae.
 * Control flow follows the pinned LVGL 9.3 lv_refr.c refr_obj body at
 * third-party/upstream/lvgl (344c7c31), with stock Main field offsets. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *, uint32_t);
extern uint32_t audio_uart_lv_scrollbar_mode_452dd8(void *);
extern uint32_t audio_uart_lv_draw_color_composite_44c54a(void *, uint32_t,
                                                           uint32_t);
extern void audio_uart_lv_obj_redraw_4531ae(void *, void *);
extern uint32_t audio_uart_lv_render_area_select_454074(void *, void *,
                                                         uint32_t, void *, void *);
extern uint32_t audio_uart_lv_render_cover_event_45417c(void *, const void *);
extern uint32_t audio_uart_lv_area_height_4515a4(const void *);
extern uint32_t audio_uart_lv_area_width_451598(const void *);
extern uint32_t audio_uart_lv_color_format_bytes_441004(uint32_t);
extern uint32_t audio_uart_lv_draw_style_metric_45311a(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_style_metric_453124(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_style_metric_45312e(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_style_metric_453138(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_style_metric_453142(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_style_metric_45314c(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_style_metric_453156(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_style_metric_453180(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_style_metric_45318c(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_style_metric_453198(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_style_metric_4531a4(void *, uint32_t);
extern void *audio_uart_lv_draw_layer_create_48475e(void *, uint32_t,
                                                      const void *);
extern void audio_uart_ambiq_image_options_init_488918(void *);
extern void audio_uart_lv_draw_layer_48895e(void *, const void *, const void *);

static uint32_t read32(const uint8_t *bytes, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(bytes + offset);
}

static void write32(uint8_t *bytes, uint32_t offset, uint32_t value)
{
    *(uint32_t *)(void *)(bytes + offset) = value;
}

static int32_t pivot_coordinate(uint32_t raw, uint32_t span)
{
    const uint32_t payload = raw & ~0x60000000u;
    if ((raw & 0x60000000u) != 0x20000000u || payload > 0x1ffffffeu)
        return (int32_t)raw;
    const int32_t percent = payload > 0x0fffffffu ?
        (int32_t)(0x0fffffffu - payload) : (int32_t)payload;
    return (int32_t)((int32_t)((uint32_t)span * (uint32_t)percent) / 100);
}

static uint32_t is_percent(uint32_t raw)
{
    return (raw & 0x60000000u) == 0x20000000u &&
           (raw & ~0x60000000u) <= 0x1ffffffeu;
}

void audio_uart_lv_draw_object_4541b6(void *layer_arg, void *object)
{
    uint8_t *const layer = (uint8_t *)layer_arg;
    uint8_t *const obj = (uint8_t *)object;
    if (audio_uart_lv_obj_has_flag_43e0e0(object, 1u) != 0u) return;
    const uint8_t layered = (uint8_t)audio_uart_lv_draw_style_metric_45318c(
        object, 0u);
    if (layered < 2u) return;

    const uint8_t original_opacity = layer[0x38u];
    const uint32_t original_recolor = read32(layer, 0x39u);
    const uint8_t object_opacity = (uint8_t)
        audio_uart_lv_draw_style_metric_453180(object, 0u);
    if (object_opacity < 253u)
        layer[0x38u] = (uint8_t)(((uint32_t)original_opacity *
                                  object_opacity) >> 8u);
    write32(layer, 0x39u, audio_uart_lv_draw_color_composite_44c54a(
        object, 0u, read32(layer, 0x39u)));

    const uint8_t type = (uint8_t)audio_uart_lv_scrollbar_mode_452dd8(object);
    if (type == 0u) {
        audio_uart_lv_obj_redraw_4531ae(layer, object);
        layer[0x38u] = original_opacity;
        write32(layer, 0x39u, original_recolor);
        return;
    }

    int32_t full[4];
    int32_t object_area[4];
    if (audio_uart_lv_render_area_select_454074(layer, object, type,
                                                  full, object_area) != 1u)
        return;
    uint32_t rgb_rows = audio_uart_lv_area_height_4515a4(full);
    uint32_t argb_rows = audio_uart_lv_area_height_4515a4(full);
    if (type == 1u) {
        const uint32_t width = audio_uart_lv_area_width_451598(full);
        const uint8_t *const display = (const uint8_t *)(uintptr_t)
            read32(audio_uart_display_lv_root, 0x10u);
        const uint32_t pixel_bytes = audio_uart_lv_color_format_bytes_441004(
            display[0x3cu]);
        rgb_rows = (0x40000u / width) / pixel_bytes;
        argb_rows = (0x40000u / width) / 4u;
    }

    int32_t tile[4] = {full[0], full[1], full[2], full[1]};
    while (tile[3] < full[3]) {
        uint32_t end = (uint32_t)tile[1] + rgb_rows - 1u;
        if ((int32_t)end > full[3]) end = (uint32_t)full[3];
        tile[3] = (int32_t)end;
        const uint32_t mask = audio_uart_lv_draw_style_metric_4531a4(object, 0u);
        const uint32_t needs_alpha = mask != 0u ||
            audio_uart_lv_render_cover_event_45417c(object, tile) != 0u;
        if (needs_alpha != 0u) {
            end = (uint32_t)tile[1] + argb_rows - 1u;
            if ((int32_t)end > full[3]) end = (uint32_t)full[3];
            tile[3] = (int32_t)end;
        }
        uint8_t *const child = (uint8_t *)audio_uart_lv_draw_layer_create_48475e(
            layer, needs_alpha != 0u ? 0x10u : 6u, tile);
        audio_uart_lv_obj_redraw_4531ae(child, object);

        uint8_t descriptor[0x6cu];
        const uint32_t pivot_x_raw = audio_uart_lv_draw_style_metric_453138(object, 0u);
        const uint32_t pivot_y_raw = audio_uart_lv_draw_style_metric_453142(object, 0u);
        const int32_t pivot_x = pivot_coordinate(pivot_x_raw,
            is_percent(pivot_x_raw) ?
            audio_uart_lv_area_width_451598(obj + 0x14u) : 0u);
        const int32_t pivot_y = pivot_coordinate(pivot_y_raw,
            is_percent(pivot_y_raw) ?
            audio_uart_lv_area_height_4515a4(obj + 0x14u) : 0u);
        audio_uart_ambiq_image_options_init_488918(descriptor);
        write32(descriptor, 0x44u,
                (uint32_t)((int32_t)read32(obj, 0x14u) + pivot_x -
                           (int32_t)read32(child, 4u)));
        write32(descriptor, 0x48u,
                (uint32_t)((int32_t)read32(obj, 0x18u) + pivot_y -
                           (int32_t)read32(child, 8u)));
        descriptor[0x50u] = layered;
        int32_t rotation = (int32_t)audio_uart_lv_draw_style_metric_45312e(
            object, 0u);
        while (rotation > 3600) rotation -= 3600;
        while (rotation < 0) rotation += 3600;
        write32(descriptor, 0x30u, (uint32_t)rotation);
        write32(descriptor, 0x34u, audio_uart_lv_draw_style_metric_45311a(object, 0u));
        write32(descriptor, 0x38u, audio_uart_lv_draw_style_metric_453124(object, 0u));
        write32(descriptor, 0x3cu, audio_uart_lv_draw_style_metric_45314c(object, 0u));
        write32(descriptor, 0x40u, audio_uart_lv_draw_style_metric_453156(object, 0u));
        descriptor[0x51u] = (uint8_t)((descriptor[0x51u] & ~7u) |
            ((uint8_t)audio_uart_lv_draw_style_metric_453198(object, 0u) & 7u));
        const uint8_t *const display = (const uint8_t *)(uintptr_t)
            read32(audio_uart_display_lv_root, 0x10u);
        uint16_t flags = *(uint16_t *)(void *)(descriptor + 0x50u);
        flags = (uint16_t)((flags & ~(1u << 11u)) |
                           (((read32(display, 0x38u) >> 16u) & 1u) << 11u));
        *(uint16_t *)(void *)(descriptor + 0x50u) = flags;
        write32(descriptor, 0x1cu, (uint32_t)(uintptr_t)child);
        write32(descriptor, 0x68u, mask);
        for (uint32_t index = 0u; index < 4u; ++index)
            write32(descriptor, 0x58u + index * 4u,
                    (uint32_t)object_area[index]);
        audio_uart_lv_draw_layer_48895e(layer, descriptor, tile);
        tile[1] = tile[3] + 1;
    }
    layer[0x38u] = original_opacity;
    write32(layer, 0x39u, original_recolor);
}
