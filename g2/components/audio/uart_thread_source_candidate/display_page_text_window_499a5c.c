/* Apollo lv_label_get_letter_on, native 0x499a5c..0x499c9d.
 * Control flow follows third-party/upstream/lvgl/src/widgets/label/lv_label.c
 * at the pinned LVGL revision; 0x499a5c was absent from the Ghidra export.
 */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);
extern void audio_uart_lv_obj_content_coords_43feca(void *, void *);
extern uint32_t audio_uart_page_text_pointer_4997f8(const void *);
extern int32_t audio_uart_lv_area_width_451598(const void *);
extern int32_t audio_uart_lv_area_height_4515a4(const void *);
extern int32_t audio_uart_page_metric_4993c0(void *, uint32_t);
extern int32_t audio_uart_page_metric_4993d4(void *, uint32_t);
extern int32_t audio_uart_page_metric_4993ca(void *, uint32_t);
extern uint32_t audio_uart_page_layout_flags_49abea(void *);
extern uint32_t audio_uart_text_line_length_4897fc(const char *, uint32_t,
    const void *, int32_t, int32_t, int32_t *, uint32_t);
extern uint64_t audio_uart_text_utf8_previous_489dbc(const char *, uint32_t *,
    uint32_t, uint32_t);
extern uint32_t audio_uart_page_text_align_class_44c448(void *, uint32_t,
    const char *);
extern void audio_uart_page_text_align_49ac4a(int32_t *, uint32_t,
    const char *, uint32_t, const void *, int32_t, const void *, uint32_t);
extern void audio_uart_text_next_glyph_489b3c(const char *, uint32_t *,
    uint32_t *, uint32_t *);
extern uint32_t audio_uart_text_hash_state_489652(uint8_t *, uint32_t);
extern int32_t audio_uart_font_glyph_advance_4d57f4(const void *, uint32_t,
    uint32_t);
extern uint64_t audio_uart_text_utf8_count_to_bytes_489e4a(const char *,
    uint32_t, uint32_t, uint32_t);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
    const char *, const char *, ...);

static const char source_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\widgets\\label\\lv_label.c";
static const char function_name[] = "lv_label_get_letter_on";
static const char assertion_format[] = "Asserted at expression: %s (%s)";

static void fatal(uint32_t line, const char *expression) {
    audio_uart_lvgl_log(3u, source_path, line, function_name,
                        assertion_format, expression, "NULL pointer");
    for (;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
}

int32_t audio_uart_page_pad_left_499388(void *page, uint32_t selector) {
    return (int32_t)audio_uart_lv_style_property_44bdea(page, selector, 0x12u);
}
int32_t audio_uart_page_pad_top_49937e(void *page, uint32_t selector) {
    return (int32_t)audio_uart_lv_style_property_44bdea(page, selector, 0x10u);
}

uint32_t audio_uart_page_text_window_499a5c(void *page,
                                              const int32_t *position,
                                              uint32_t bidi) {
    (void)bidi; /* The stock build has LV_USE_BIDI disabled. */
    if (page == 0) fatal(0x19cu, "obj != NULL");
    if (position == 0) fatal(0x19du, "pos_in != NULL");
    const int32_t x_position = position[0] - audio_uart_page_pad_left_499388(page, 0u);
    const int32_t y_position = position[1] - audio_uart_page_pad_top_49937e(page, 0u);
    int32_t area[4] = {0, 0, 0, 0};
    audio_uart_lv_obj_content_coords_43feca(page, area);
    const char *text = (const char *)(uintptr_t)audio_uart_page_text_pointer_4997f8(page);
    uint32_t line_start = 0u;
    uint32_t next_line_start = 0u;
    const int32_t max_width = audio_uart_lv_area_width_451598(area);
    const int32_t max_height = audio_uart_lv_area_height_4515a4(area);
    const void *font = (const void *)(uintptr_t)(uint32_t)audio_uart_page_metric_4993c0(page, 0u);
    const int32_t line_space = audio_uart_page_metric_4993d4(page, 0u);
    const int32_t letter_space = audio_uart_page_metric_4993ca(page, 0u);
    const int32_t letter_height = *(const int32_t *)((const uint8_t *)font + 0xcu);
    uint32_t flags = audio_uart_page_layout_flags_49abea(page) & 0xffu;
    int32_t y = 0;
    while (text[line_start] != '\0') {
        const int last_line = y + letter_height + line_space + letter_height > max_height;
        if (last_line && (((const uint8_t *)page)[0x5cu] & 15u) == 1u) flags |= 4u;
        next_line_start += audio_uart_text_line_length_4897fc(text + line_start,
            0xffffffffu, font, letter_space, max_width, 0, flags);
        if (y_position <= y + letter_height) {
            uint32_t previous = next_line_start;
            const uint32_t letter = (uint32_t)audio_uart_text_utf8_previous_489dbc(
                text, &previous, 0u, 0u);
            if (letter != '\n' && text[next_line_start] == '\0') next_line_start++;
            break;
        }
        y += letter_height + line_space;
        line_start = next_line_start;
    }
    const char *line = text + line_start;
    const uint32_t alignment = audio_uart_page_text_align_class_44c448(page, 0u, text) & 0xffu;
    int32_t x = 0;
    audio_uart_page_text_align_49ac4a(&x, alignment, line,
        next_line_start - line_start, font, letter_space, area, flags);
    uint8_t command_state = 0u;
    uint32_t i = 0u;
    uint32_t i_active = 0u;
    if (next_line_start != 0u) {
        while (i + line_start < next_line_start) {
            uint32_t letter = 0u;
            uint32_t next_letter = 0u;
            audio_uart_text_next_glyph_489b3c(line, &letter, &next_letter, &i);
            if ((flags & 8u) != 0u &&
                audio_uart_text_hash_state_489652(&command_state,
                    (uint8_t)line[i]) != 0u) continue;
            const int32_t width = audio_uart_font_glyph_advance_4d57f4(
                font, letter, next_letter);
            if (x_position < x + width || i + line_start == next_line_start ||
                text[i_active + line_start] == '\0') {
                i = i_active;
                break;
            }
            x += width + letter_space;
            i_active = i;
        }
    }
    return (uint32_t)audio_uart_text_utf8_count_to_bytes_489e4a(line, i, 0u, 0u) +
           (uint32_t)audio_uart_text_utf8_count_to_bytes_489e4a(text, line_start, 0u, 0u);
}
