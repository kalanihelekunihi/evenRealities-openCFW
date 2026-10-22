/* QuickList page text helpers (product UI TU around 0x4f4f5c..0x4f9xxx; no source path retained).
 * Native 0x4f5050..0x4f5068 and 0x4f50d6..0x4f517c.
 *
 * 0x4f5050/0x4f505c are IAR out-of-line copies of the LVGL 9.3
 * lv_obj_style_gen.h inlines lv_obj_get_style_bg_opa / lv_obj_get_style_opa
 * owned by this TU (callers 0x4f74f8, 0x4f7634, 0x4f76b6). 0x4f50d6 measures a
 * wrapped string and returns its line count (caller 0x4f891c passes max width
 * 283, no spacing, at most two lines). */
#include <stdint.h>
#include <stddef.h>

#define G2_LV_STYLE_BG_OPA 29u
#define G2_LV_STYLE_OPA 98u
#define G2_TEXT_FALLBACK_LINE_HEIGHT 28 /* used for NULL/empty input and lh < 1 */

typedef struct {
    int32_t x;
    int32_t y;
} g2_lv_point_t;

/* lv_font_t (LVGL 9.3): three callbacks, then line_height at +0xc. */
typedef struct {
    void *get_glyph_dsc;      /* +0x0 */
    void *get_glyph_bitmap;   /* +0x4 */
    void *release_glyph;      /* +0x8 */
    int32_t line_height;      /* +0xc */
} g2_lv_font_head_t;

extern uint32_t audio_uart_lv_style_property_44bdea(void *obj, uint32_t part,
                                                    uint32_t prop);   /* lv_obj_get_style_prop */
extern uint32_t g2_log_module_length(const char *text);              /* strlen 0x44a43c */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void audio_uart_page_event_calculate_489546(void *size, const char *text,
    const void *font, int32_t letter_space, int32_t line_space, int32_t max_width,
    uint32_t flags);                                                 /* lv_text_get_size */

uint8_t lv_obj_get_style_bg_opa_4f5050(void *obj, uint32_t part)
{
    return (uint8_t)audio_uart_lv_style_property_44bdea(obj, part, G2_LV_STYLE_BG_OPA);
}

uint8_t lv_obj_get_style_opa_4f505c(void *obj, uint32_t part)
{
    return (uint8_t)audio_uart_lv_style_property_44bdea(obj, part, G2_LV_STYLE_OPA);
}

/* Returns the number of wrapped lines (at least 1, clamped to max_lines when
 * max_lines > 0) and stores lines * line pitch in *out_height when given. */
int32_t quicklist_text_line_count_4f50d6(const char *text, const void *font,
                                         int32_t max_width, int32_t letter_space,
                                         int32_t line_space, int32_t max_lines,
                                         int32_t *out_height)
{
    g2_lv_point_t size;
    int32_t pitch;
    int32_t lines;

    if (text == NULL || font == NULL || g2_log_module_length(text) == 0u) {
        if (out_height != NULL)
            *out_height = G2_TEXT_FALLBACK_LINE_HEIGHT;
        return 1;
    }

    aeabi_memset_43c0e4(&size, sizeof size, 0);
    audio_uart_page_event_calculate_489546(&size, text, font, letter_space, line_space,
                                           max_width, 0u);
    pitch = line_space + ((const g2_lv_font_head_t *)font)->line_height;
    if (pitch < 1)
        pitch = G2_TEXT_FALLBACK_LINE_HEIGHT;
    lines = (pitch + size.y - 1) / pitch;
    if (lines < 1)
        lines = 1;
    if (max_lines >= 1 && max_lines < lines)
        lines = max_lines;
    if (out_height != NULL)
        *out_height = pitch * lines;
    return lines;
}
