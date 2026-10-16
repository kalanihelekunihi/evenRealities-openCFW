/* Native Apollo label layout 0x49a602: full source candidate.
 * The mode 1 text-window provider is source-owned at 0x499a5c.
 */
#include <stdint.h>

extern void audio_uart_lv_obj_content_coords_43feca(void *, void *);
extern int32_t audio_uart_lv_area_width_451598(const void *);
extern int32_t audio_uart_page_metric_4993c0(void *, uint32_t);
extern int32_t audio_uart_page_metric_4993d4(void *, uint32_t);
extern int32_t audio_uart_page_metric_4993ca(void *, uint32_t);
extern uint64_t audio_uart_page_layout_flags_49abea(void *, uint32_t,
    uint32_t, uint32_t);
extern void audio_uart_page_event_prepare_49aacc(void *);
extern void audio_uart_page_event_calculate_489546(void *, const char *,
    const void *, int32_t, int32_t, int32_t, uint32_t);
extern void audio_uart_page_relayout_43ffa0(void *);
extern void audio_uart_page_invalidate_440656(void *);
extern int32_t audio_uart_page_metric_499402(void *, uint32_t);
extern int32_t audio_uart_page_metric_49940c(void *, uint32_t);
extern int32_t audio_uart_lv_anim_duration_clamp_4505a2(uint32_t, uint32_t, uint32_t);
extern void audio_uart_lv_anim_init_4503d6(void *);
extern void audio_uart_lv_anim_values_4506ce(void *, int32_t, int32_t);
extern void *audio_uart_page_lv_anim_lookup_450566(void *, const void *);
extern int32_t audio_uart_lv_anim_speed_to_time_4506fc(int32_t, int32_t, int32_t);
extern void audio_uart_page_layout_copy_anim_49a5c0(void *, const void *, uint32_t);
extern void audio_uart_lv_anim_start_450408(void *);
extern void audio_uart_lv_style_unlink_450500(void *, const void *);
extern int32_t audio_uart_lv_area_height_4515a4(const void *);
extern uint32_t audio_uart_font_glyph_advance_4d57f4(int32_t, uint32_t, uint32_t);
extern uint64_t audio_uart_text_utf8_count_489e6e(const char *, uint32_t,
    uint32_t, uint32_t);
extern uint64_t audio_uart_text_utf8_bytes_for_count_489e14(const char *,
    uint32_t, uint32_t, uint32_t);
extern uint64_t audio_uart_text_utf8_previous_489dbc(const char *, uint32_t *,
    uint32_t, uint32_t);
extern uint32_t audio_uart_lv_string_length_454768(const char *);
extern uint32_t audio_uart_page_text_window_499a5c(void *, const int32_t *, uint32_t);
extern void audio_uart_page_event_finish_49ab06(void *, uint32_t);

#define SCROLL_X ((const void *)(uintptr_t)0x49abbdu)
#define SCROLL_Y ((const void *)(uintptr_t)0x49abc9u)
#define audio_uart_page_geometry_43feca audio_uart_lv_obj_content_coords_43feca
#define audio_uart_geometry_width_451598 audio_uart_lv_area_width_451598
#define audio_uart_text_measure_489546 audio_uart_page_event_calculate_489546
#define audio_uart_page_geometry_finish_43ffa0 audio_uart_page_relayout_43ffa0
#define audio_uart_page_layout_invalidate_440656 audio_uart_page_invalidate_440656
#define audio_uart_anim_duration_4505a2 audio_uart_lv_anim_duration_clamp_4505a2
#define audio_uart_anim_init_4503d6 audio_uart_lv_anim_init_4503d6
#define audio_uart_anim_set_values_4506ce audio_uart_lv_anim_values_4506ce
#define audio_uart_anim_find_450566 audio_uart_page_lv_anim_lookup_450566
#define audio_uart_anim_limit_4506fc audio_uart_lv_anim_speed_to_time_4506fc
#define audio_uart_anim_start_450408 audio_uart_lv_anim_start_450408
#define audio_uart_anim_delete_450500 audio_uart_lv_style_unlink_450500
#define audio_uart_geometry_height_4515a4 audio_uart_lv_area_height_4515a4
#define audio_uart_font_count_character_4d57f4 audio_uart_font_glyph_advance_4d57f4
#define audio_uart_text_utf8_length_454768 audio_uart_lv_string_length_454768

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u);
    p[3] = (uint8_t)(value >> 24u);
}

void audio_uart_page_layout_update_49a602(void *page) {
    uint8_t *p = (uint8_t *)page;
    uint32_t mode = p[0x5cu] & 15u;
    const uint32_t text = get32(p + 0x2cu);
    if (text == 0u) return;
    put32(p + 0x38u, 0xffffffffu);
    p[0x5cu] |= 0x80u;
    uint32_t geometry[4] = {0u, 0u, 0u, 0u};
    uint32_t measured[2] = {0u, 0u};
    audio_uart_page_geometry_43feca(page, geometry);
    const int32_t available_width = audio_uart_geometry_width_451598(geometry);
    const int32_t font = audio_uart_page_metric_4993c0(page, 0u);
    const int32_t font_spacing = audio_uart_page_metric_4993d4(page, 0u);
    const int32_t spacing = audio_uart_page_metric_4993ca(page, 0u);
    const uint32_t flags = (uint32_t)audio_uart_page_layout_flags_49abea(
        page, 0u, 0u, 0u) & 0xffu;
    audio_uart_page_event_prepare_49aacc(page);
    audio_uart_text_measure_489546(measured, (const char *)(uintptr_t)text,
                                   (const void *)(uintptr_t)(uint32_t)font,
                                   spacing, font_spacing, available_width,
                                   flags);
    audio_uart_page_geometry_finish_43ffa0(page);
    if (mode == 2u) {
        const int32_t style = audio_uart_page_metric_499402(page, 0u);
        int32_t duration = audio_uart_page_metric_49940c(page, 0u);
        if (duration == 0) duration = audio_uart_anim_duration_4505a2(40u, 300u, 10000u);
        uint32_t descriptor[0x60u / 4u];
        audio_uart_anim_init_4503d6(descriptor);
        uint8_t *d = (uint8_t *)descriptor;
        put32(d, (uint32_t)(uintptr_t)page);
        put32(d + 0x44u, 0xffffffffu);
        put32(d + 0x38u, 300u);
        put32(d + 0x40u, 300u);
        int horizontal_started = 0;
        if (audio_uart_geometry_width_451598(geometry) < (int32_t)measured[0]) {
            const int32_t delta = audio_uart_geometry_width_451598(geometry) -
                                  (int32_t)measured[0];
            audio_uart_anim_set_values_4506ce(descriptor, 0, delta);
            put32(d + 4u, (uint32_t)(uintptr_t)SCROLL_X);
            const uint8_t *old = (const uint8_t *)audio_uart_anim_find_450566(page, SCROLL_X);
            int32_t offset = old ? (int32_t)get32(old + 0x34u) : 0;
            int32_t limit = audio_uart_anim_limit_4506fc(duration, 0, delta);
            if (limit < offset) offset = limit;
            if (old && (old[0x5cu] & 2u)) {
                d[0x5cu] |= 2u;
                const uint32_t a = get32(d + 0x24u);
                put32(d + 0x24u, get32(d + 0x2cu));
                put32(d + 0x2cu, a);
            }
            put32(d + 0x30u, (uint32_t)duration);
            put32(d + 0x34u, (uint32_t)offset);
            put32(d + 0x3cu, (uint32_t)duration);
            if (style != 0)
                audio_uart_page_layout_copy_anim_49a5c0(descriptor,
                    (const void *)(uintptr_t)(uint32_t)style, mode);
            audio_uart_anim_start_450408(descriptor);
            if (offset < 0) put32(p + 0x54u, 0u);
            horizontal_started = 1;
        } else {
            audio_uart_anim_delete_450500(page, SCROLL_X);
            put32(p + 0x54u, 0u);
        }
        if ((int32_t)measured[1] <= audio_uart_geometry_height_4515a4(geometry) ||
            horizontal_started) {
            audio_uart_anim_delete_450500(page, SCROLL_Y);
            put32(p + 0x58u, 0u);
        } else {
            const int32_t delta = audio_uart_geometry_height_4515a4(geometry) -
                                  (int32_t)measured[1] -
                                  (int32_t)get32((const uint8_t *)(uintptr_t)(uint32_t)font + 0xcu);
            audio_uart_anim_set_values_4506ce(descriptor, 0, delta);
            put32(d + 4u, (uint32_t)(uintptr_t)SCROLL_Y);
            const uint8_t *old = (const uint8_t *)audio_uart_anim_find_450566(page, SCROLL_Y);
            int32_t offset = old ? (int32_t)get32(old + 0x34u) : 0;
            if ((int32_t)get32(d + 0x30u) < offset)
                offset = (int32_t)get32(d + 0x30u);
            put32(d + 0x34u, (uint32_t)offset);
            if (old && (old[0x5cu] & 2u)) {
                d[0x5cu] |= 2u;
                const uint32_t a = get32(d + 0x24u);
                put32(d + 0x24u, get32(d + 0x2cu));
                put32(d + 0x2cu, a);
            }
            put32(d + 0x30u, (uint32_t)duration);
            put32(d + 0x3cu, (uint32_t)duration);
            if (style != 0)
                audio_uart_page_layout_copy_anim_49a5c0(descriptor,
                    (const void *)(uintptr_t)(uint32_t)style, mode);
            audio_uart_anim_start_450408(descriptor);
        }
    } else if (mode == 3u) {
        const int32_t style = audio_uart_page_metric_499402(page, 0u);
        int32_t duration = audio_uart_page_metric_49940c(page, 0u);
        if (duration == 0) duration = audio_uart_anim_duration_4505a2(40u, 300u, 10000u);
        uint32_t descriptor[0x60u / 4u];
        audio_uart_anim_init_4503d6(descriptor);
        uint8_t *d = (uint8_t *)descriptor;
        put32(d + 0x44u, 0xffffffffu);
        put32(d, (uint32_t)(uintptr_t)page);
        int horizontal_started = 0;
        if (audio_uart_geometry_width_451598(geometry) < (int32_t)measured[0]) {
            const uint32_t spaces = audio_uart_font_count_character_4d57f4(font, 32u, 32u) & 0xffffu;
            audio_uart_anim_set_values_4506ce(descriptor, 0,
                -(int32_t)(3u * spaces) - (int32_t)measured[0]);
            put32(d + 4u, (uint32_t)(uintptr_t)SCROLL_X);
            put32(d + 0x30u, (uint32_t)duration);
            const uint8_t *old = (const uint8_t *)audio_uart_anim_find_450566(page, SCROLL_X);
            int32_t old_offset = old ? (int32_t)get32(old + 0x34u) : 0;
            const int32_t limit = audio_uart_anim_limit_4506fc(duration,
                (int32_t)get32(d + 0x24u), (int32_t)get32(d + 0x2cu));
            if (old_offset < limit) put32(d + 0x34u, (uint32_t)old_offset);
            if (style != 0)
                audio_uart_page_layout_copy_anim_49a5c0(descriptor,
                    (const void *)(uintptr_t)(uint32_t)style, mode);
            audio_uart_anim_start_450408(descriptor);
            horizontal_started = 1;
        } else {
            audio_uart_anim_delete_450500(page, SCROLL_X);
            put32(p + 0x54u, 0u);
        }
        if ((int32_t)measured[1] <= audio_uart_geometry_height_4515a4(geometry) ||
            horizontal_started) {
            audio_uart_anim_delete_450500(page, SCROLL_Y);
            put32(p + 0x58u, 0u);
        } else {
            audio_uart_anim_set_values_4506ce(descriptor, 0,
                -(int32_t)get32((const uint8_t *)(uintptr_t)(uint32_t)font + 0xcu) -
                (int32_t)measured[1]);
            put32(d + 4u, (uint32_t)(uintptr_t)SCROLL_Y);
            put32(d + 0x30u, (uint32_t)duration);
            const uint8_t *old = (const uint8_t *)audio_uart_anim_find_450566(page, SCROLL_Y);
            const int32_t old_offset = old ? (int32_t)get32(old + 0x34u) : 0;
            if (style == 0) {
                if (old_offset < (int32_t)get32(d + 0x30u))
                    put32(d + 0x34u, (uint32_t)old_offset);
            } else {
                audio_uart_page_layout_copy_anim_49a5c0(descriptor,
                    (const void *)(uintptr_t)(uint32_t)style, mode);
            }
            audio_uart_anim_start_450408(descriptor);
        }
    } else if (mode == 1u) {
        const int32_t height = audio_uart_geometry_height_4515a4(geometry);
        const int32_t font_height = (int32_t)get32(
            (const uint8_t *)(uintptr_t)(uint32_t)font + 0xcu);
        if (height < (int32_t)measured[1] && font_height < (int32_t)measured[1] &&
            (uint32_t)audio_uart_text_utf8_count_489e6e(
                (const char *)(uintptr_t)text, 0u, 0u, 0u) > 3u) {
            const int32_t width = audio_uart_geometry_width_451598(geometry);
            const uint32_t dot_width = audio_uart_font_count_character_4d57f4(font, 46u, 46u) & 0xffffu;
            int32_t positions[2];
            positions[0] = width - 3 * (spacing + (int32_t)dot_width);
            const int32_t stride = font_spacing + font_height;
            const int32_t layout_height = audio_uart_geometry_height_4515a4(geometry);
            const int32_t remainder = layout_height - stride * (layout_height / stride);
            positions[1] = (remainder < font_height) ?
                layout_height - remainder - font_spacing : font_height + layout_height - remainder;
            const uint32_t window = audio_uart_page_text_window_499a5c(page, positions, 0u);
            const char *content = (const char *)(uintptr_t)text;
            const uint32_t text_length = audio_uart_text_utf8_length_454768(content);
            uint32_t bytes = (uint32_t)audio_uart_text_utf8_bytes_for_count_489e14(
                content, window, 0u, 0u);
            while (text_length < bytes + 3u)
                (void)audio_uart_text_utf8_previous_489dbc(content, &bytes, 0u, 0u);
            audio_uart_page_event_finish_49ab06(page, bytes);
        }
    }
    audio_uart_page_layout_invalidate_440656(page);
}
