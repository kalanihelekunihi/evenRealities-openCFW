/* Apollo LVGL label draw_main 0x49a31c..0x49a5bf.
 * Reconstructed against pinned LVGL src/widgets/label/lv_label.c draw_main.
 */
#include <stdint.h>

extern void *audio_uart_lv_event_layer_451960(void *);
extern void audio_uart_lv_obj_content_coords_43feca(void *, void *);
extern uint64_t audio_uart_page_layout_flags_49abea(void *, uint32_t,
    uint32_t, uint32_t);
extern void audio_uart_lv_image_descriptor_init_489f5e(void *);
extern int32_t audio_uart_lv_area_height_4515a4(const void *);
extern int32_t audio_uart_lv_area_width_451598(const void *);
extern void audio_uart_lv_draw_label_dsc_init_452988(void *, uint32_t, void *);
extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);
extern void audio_uart_page_event_calculate_489546(void *, const char *,
    const void *, int32_t, int32_t, int32_t, uint32_t);
extern uint32_t audio_uart_lv_area_intersect_450bcc(void *, const void *,
    const void *);
extern int32_t audio_uart_lv_scroll_top_44e4aa(void *);
extern void audio_uart_ambiq_area_move_450bb2(void *, int32_t, int32_t);
extern void audio_uart_lv_draw_label_489fe0(void *, const void *, const void *);
extern int32_t audio_uart_font_glyph_advance_4d57f4(const void *, uint32_t,
    uint32_t);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u); p[3] = (uint8_t)(v >> 24u);
}
static void put24(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u);
}
static void copy16(uint8_t *destination, const uint8_t *source) {
    for (uint32_t i = 0u; i < 16u; ++i) destination[i] = source[i];
}

void audio_uart_page_event_dispatch_49a31c(void *event) {
    uint8_t *page = (uint8_t *)(uintptr_t)get32((const uint8_t *)event);
    uint8_t *layer = (uint8_t *)audio_uart_lv_event_layer_451960(event);
    uint32_t frame_words[0xb0u / 4u] = {0};
    uint8_t *frame = (uint8_t *)frame_words;
    uint8_t *area = frame + 0x14u;
    uint8_t *descriptor = frame + 0x2cu;
    uint8_t *clip = frame + 0x90u;
    uint8_t *backup = frame + 0xa0u;
    uint8_t *layer_clip = layer + 0x18u;
    audio_uart_lv_obj_content_coords_43feca(page, area);
    const uint32_t flags = (uint32_t)audio_uart_page_layout_flags_49abea(
        page, 0u, 0u, 0u) & 0xffu;
    audio_uart_lv_image_descriptor_init_489f5e(descriptor);
    put32(frame + 0x48u, get32(page + 0x2cu));
    frame[0x80u] = (uint8_t)((frame[0x80u] & ~2u) |
                             (((page[0x5cu] >> 4u) & 1u) << 1u));
    put32(frame + 0x5cu, get32(page + 0x54u));
    put32(frame + 0x60u, get32(page + 0x58u));
    const uint32_t mode = page[0x5cu] & 15u;
    if (mode != 3u && audio_uart_lv_area_height_4515a4(area) >= 1024)
        put32(frame + 0x84u, (uint32_t)(uintptr_t)(page + 0x38u));
    frame[0x7fu] = (uint8_t)((frame[0x7fu] & 7u) | (flags << 3u));
    put32(frame + 0x3cu, (uint32_t)(uintptr_t)layer);
    audio_uart_lv_draw_label_dsc_init_452988(page, 0u, descriptor);
    if (frame[0x7du] == 0u) frame[0x7du] = 1u;
    const uint32_t selection_start = get32(page + 0x44u);
    const uint32_t selection_end = get32(page + 0x48u);
    put32(frame + 0x68u, selection_start);
    put32(frame + 0x6cu, selection_end);
    if (selection_start != 0xffffu && selection_end != 0xffffu) {
        put24(frame + 0x70u,
              audio_uart_lv_style_property_44bdea(page, 0x40000u, 0x58u));
        put24(frame + 0x73u,
              audio_uart_lv_style_property_44bdea(page, 0x40000u, 0x1cu));
    }
    put24(frame + 0x89u,
          audio_uart_lv_style_property_44bdea(page, 0u, 0x61u));
    frame[0x88u] = (uint8_t)audio_uart_lv_style_property_44bdea(page, 0u, 0x60u);
    put32(frame + 0x8cu,
          audio_uart_lv_style_property_44bdea(page, 0u, 0x5fu));
    const void *font = (const void *)(uintptr_t)get32(frame + 0x4cu);
    const int32_t letter_spacing = (int32_t)get32(frame + 0x58u);
    const int32_t line_spacing = (int32_t)get32(frame + 0x54u);
    const char *text = (const char *)(uintptr_t)get32(page + 0x2cu);
    if ((mode == 2u || mode == 3u) &&
        (frame[0x7du] == 2u || frame[0x7du] == 3u)) {
        audio_uart_page_event_calculate_489546(frame + 0x24u, text, font,
            letter_spacing, line_spacing, 0x1fffffffu, flags);
        if (audio_uart_lv_area_width_451598(area) < (int32_t)get32(frame + 0x24u))
            frame[0x7du] = 1u;
    }
    if (audio_uart_lv_area_intersect_450bcc(clip, area, layer_clip) == 0u)
        return;
    if (mode == 0u) {
        const int32_t scroll = audio_uart_lv_scroll_top_44e4aa(page);
        audio_uart_ambiq_area_move_450bb2(area, 0, -scroll);
        put32(area + 0xcu, get32(page + 0x20u));
    }
    if (mode == 2u || mode == 3u || mode == 4u) {
        copy16(backup, layer_clip);
        copy16(layer_clip, clip);
        audio_uart_lv_draw_label_489fe0(layer, descriptor, area);
        copy16(layer_clip, backup);
    } else {
        audio_uart_lv_draw_label_489fe0(layer, descriptor, area);
    }
    copy16(backup, layer_clip);
    copy16(layer_clip, clip);
    if (mode == 3u) {
        audio_uart_page_event_calculate_489546(frame + 0xcu, text, font,
            letter_spacing, line_spacing, 0x1fffffffu, flags);
        const int32_t measured_width = (int32_t)get32(frame + 0xcu);
        const int32_t measured_height = (int32_t)get32(frame + 0x10u);
        if (audio_uart_lv_area_width_451598(area) < measured_width) {
            const int32_t space = audio_uart_font_glyph_advance_4d57f4(font, 32u, 32u) & 0xffffu;
            put32(frame + 0x5cu, (uint32_t)(measured_width + 3 * space +
                                             (int32_t)get32(page + 0x54u)));
            put32(frame + 0x60u, get32(page + 0x58u));
            audio_uart_lv_draw_label_489fe0(layer, descriptor, area);
        }
        if (audio_uart_lv_area_height_4515a4(area) < measured_height) {
            put32(frame + 0x5cu, get32(page + 0x54u));
            put32(frame + 0x60u,
                  (uint32_t)((int32_t)get32((const uint8_t *)font + 0xcu) +
                             measured_height + (int32_t)get32(page + 0x58u)));
            audio_uart_lv_draw_label_489fe0(layer, descriptor, area);
        }
    }
    copy16(layer_clip, backup);
}
