/* Terminal query panel scroll alignment, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\terminal\terminal_query_panel_ui.c.
 * Native 0x5eb47a..0x5eb575 and 0x5eb646..0x5eb8d9; literal pool
 * 0x5ebc34..0x5ebc53 (shared with the rest of the file).
 *
 * The panel (+0x214) scrolls a column whose option list (+0x21c) follows the
 * question text. Option rows are positioned relative to the list, so
 * absolute y = lv_obj_get_y(list) + lv_obj_get_y(row). The view height is the
 * panel height minus its top/bottom padding (falling back to the full height
 * when that is not positive). */
#include <stdint.h>
#include "terminal_ui_a67.h"

#define QUERY_BOTTOM_GAP 8   /* desired space below the selected option incl. pad_bottom */
#define QUERY_SAFE_EXTRA 2

extern uint32_t audio_terminal_query_count_5eb30c(void);
extern int32_t audio_terminal_query_height_5eb438(uint8_t *state);
extern uint32_t audio_terminal_query_style_16_5eb2a8(void *object, uint32_t selector); /* pad_top */
extern uint32_t audio_terminal_query_style_17_5eb2b2(void *object, uint32_t selector); /* pad_bottom */
extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index); /* lv_obj_get_child */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);                  /* lv_obj_get_y */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);             /* lv_obj_get_height */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                  /* lv_obj_get_scroll_y */
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *obj);          /* lv_obj_get_scroll_bottom */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "terminal.ui"; /* ROM 0x78c59c */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_query_panel_ui.c"; /* ROM 0x6f0448 */
static const char target_fn[] = "terminal_ui_query_panel_get_selected_target_y"; /* ROM 0x7397f4 */
static const char clamp_fmt[] = "query align before clamp: idx=%u keep2=%d panel_h=%d view_h=%d pad_t=%d pad_b=%d gap_b=%d safe=%d options_top=%d sel_bottom=%d anchor_bottom=%d target_y=%d max_y=%d browsing=%d"; /* ROM 0x6d2248 */
static const char clamp_fmt_short[] = "[terminal.ui]query align before clamp: idx=%u keep2=%d panel_h=%d view_h=%d pad_t=%d pad_b=%d gap_b=%d safe=%d options_top=%d sel_bottom=%d anchor_bottom=%d target_y=%d max_y=%d browsing=%d"; /* ROM 0x6d1788 */
static const char target_fmt[] = "query align target: idx=%u target_y=%d"; /* ROM 0x74f62c */
static const char target_fmt_short[] = "[terminal.ui]query align target: idx=%u target_y=%d"; /* ROM 0x72ebac */

#define LOG_COMPRESSED() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

/* True when option idx overlaps the view for a panel scrolled to scroll_y. */
uint8_t terminal_ui_query_item_visible_5eb47a(uint8_t idx, int32_t scroll_y)
{
    g2_terminal_ui_t *ui = G2_TERMINAL_UI;
    if (ui->query_panel == NULL || ui->query_options == NULL)
        return 0u;
    if (idx >= (uint8_t)audio_terminal_query_count_5eb30c())
        return 0u;
    void *row = audio_uart_lv_child_get_44dce2(ui->query_options, idx);
    if (row == NULL)
        return 0u;
    int32_t view_end = audio_terminal_query_height_5eb438(audio_terminal_ui_state_base) + scroll_y;
    int32_t list_y = audio_uart_lv_obj_y_43fce0(ui->query_options);
    int32_t top = audio_uart_lv_obj_y_43fce0(row) + list_y;
    int32_t bottom = audio_uart_lv_obj_height_43fdda(row) + top;
    return (uint8_t)(scroll_y < bottom && top < view_end);
}

/* Highest scroll_y that still keeps the second option's top inside the view
 * (clamped to the panel's scroll range); 0 with fewer than two options. */
int32_t terminal_ui_query_first_option_limit_5eb4f6(void)
{
    g2_terminal_ui_t *ui = G2_TERMINAL_UI;
    uint8_t count = (uint8_t)audio_terminal_query_count_5eb30c();
    if (ui->query_panel == NULL || ui->query_options == NULL || count < 2u)
        return 0;
    void *row = audio_uart_lv_child_get_44dce2(ui->query_options, 1);
    if (row == NULL)
        return 0;
    int32_t view_h = audio_terminal_query_height_5eb438(audio_terminal_ui_state_base);
    int32_t list_y = audio_uart_lv_obj_y_43fce0(ui->query_options);
    int32_t limit = audio_uart_lv_obj_y_43fce0(row) + list_y - view_h + 1;
    if (limit < 0)
        limit = 0;
    int32_t y = audio_uart_lv_obj_y_44e498(ui->query_panel);
    int32_t max = audio_uart_lv_scroll_bottom_44e4bc(ui->query_panel) + y;
    if (max < 0)
        max = 0;
    if (max < limit)
        limit = max;
    return limit;
}

/* Scroll position that shows option idx with a small gap below it; with keep2
 * the following option is kept fully visible as well. */
int32_t terminal_ui_query_panel_get_selected_target_y_5eb646(uint8_t idx, uint8_t keep2)
{
    g2_terminal_ui_t *ui = G2_TERMINAL_UI;
    if (ui->query_panel == NULL || ui->query_options == NULL)
        return 0;
    uint32_t count = audio_terminal_query_count_5eb30c();
    if (idx >= (uint8_t)count)
        return 0;
    void *row = audio_uart_lv_child_get_44dce2(ui->query_options, idx);
    if (row == NULL)
        return 0;
    int32_t panel_h = audio_uart_lv_obj_height_43fdda(ui->query_panel);
    int32_t pad_t = (int32_t)audio_terminal_query_style_16_5eb2a8(ui->query_panel, 0u);
    int32_t pad_b = (int32_t)audio_terminal_query_style_17_5eb2b2(ui->query_panel, 0u);
    int32_t view_h = panel_h - pad_t - pad_b;
    if (view_h < 1)
        view_h = panel_h;
    int32_t options_top = audio_uart_lv_obj_y_43fce0(ui->query_options);
    int32_t sel_top = audio_uart_lv_obj_y_43fce0(row) + options_top;
    int32_t sel_y = audio_uart_lv_obj_y_43fce0(row) + options_top;
    int32_t sel_bottom = audio_uart_lv_obj_height_43fdda(row) + sel_y;
    int32_t gap_b = QUERY_BOTTOM_GAP - pad_b;
    if (gap_b < 0)
        gap_b = 0;
    int32_t safe = gap_b + QUERY_SAFE_EXTRA;
    int32_t anchor_bottom;
    if (keep2 != 0u && (uint32_t)idx < (uint32_t)(uint8_t)count - 1u) {
        void *next = audio_uart_lv_child_get_44dce2(ui->query_options, idx + 1);
        if (next != NULL) {
            int32_t next_top = audio_uart_lv_obj_y_43fce0(next) + options_top;
            anchor_bottom = audio_uart_lv_obj_height_43fdda(next) + next_top;
        } else {
            anchor_bottom = sel_bottom;
        }
    } else {
        anchor_bottom = safe + sel_bottom;
    }
    int32_t target = anchor_bottom - view_h;
    if (target < 0)
        target = 0;
    int32_t y = audio_uart_lv_obj_y_44e498(ui->query_panel);
    int32_t max_y = audio_uart_lv_scroll_bottom_44e4bc(ui->query_panel) + y;
    if (max_y < 0)
        max_y = 0;
    int32_t min_target = safe + sel_bottom - view_h;
    int32_t max_target = sel_top - QUERY_BOTTOM_GAP;
    if (target < min_target)
        target = min_target;
    if (max_target < target)
        target = max_target;
    if (target < 0)
        target = 0;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, target_fn, 337u, clamp_fmt, idx, keep2, panel_h,
                           view_h, pad_t, pad_b, gap_b, safe, options_top, sel_bottom, anchor_bottom, target,
                           max_y, ui->query_browsing);
    /* The stock argument-count field is computed from anchor_bottom (the
     * log macro's arity counter overflows with 14 arguments). */
    if (LOG_COMPRESSED())
        (void)compress_log_output((((uint32_t)anchor_bottom & 15u) << 22) | 0xc000000u, clamp_fmt_short,
                                  clamp_fmt_short, idx, keep2, panel_h, view_h, pad_t, pad_b, gap_b, safe,
                                  options_top, sel_bottom, anchor_bottom, target, max_y, ui->query_browsing);
    if (max_y < target)
        target = max_y;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, target_fn, 341u, target_fmt, idx, target);
    if (LOG_COMPRESSED())
        (void)compress_log_output(0xc800000u, target_fmt_short, target_fmt_short, idx, target);
    return target;
}
