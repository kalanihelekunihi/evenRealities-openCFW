/* Conversate main page input handling, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate_ui_main_page.c.
 * Native 0x5b23e4..0x5b24df, 0x5b24e8..0x5b2641, 0x5b2642..0x5b2651 and
 * 0x5b2652..0x5b29bb (literal pools at 0x5b2d2c.., 0x5b3098.., 0x5b3330..,
 * 0x5b3384.., 0x5b349c, 0x5b34cc).
 *
 * The scroll checks return the scroll step (1) or 0 when blocked; the input
 * handler forwards the result to the Conversate action reporter
 * (0x0e scroll up, 0x0f scroll down, 0x0c select, 0x06/0x08 click on the
 * top button / a list button, 0x0d unselect). */
#include <stdint.h>
#include <stddef.h>
#include "conversate_ui_context.h"

#define LOG_MODULE module
#define LOG_PATH path

extern uint32_t audio_conversate_ui_list_count_5b0c18(void);
extern uint8_t teleprompt_file_request_busy_5897e0(void); /* list animation playing */
extern uint32_t audio_uart_lv_child_count_44ddea(void *object); /* lv_obj_get_child_count */
extern void audio_conversate_report_5b02e4(uint32_t event, uint32_t value);
extern void system_close_page_factory_0046ae9c(uint32_t style, int32_t app_id);
extern void conversate_timer_mgr_reset_select_timeout_5b3c70(void);

static const char module[] = "conversate.ui"; /* ROM 0x785840 */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_main_page.c"; /* ROM 0x6e6ea4 */
static const char up_fn[] = "conversate_list_scroll_up_value_get";       /* ROM 0x752ef8 */
static const char down_fn[] = "conversate_list_scroll_down_value_get";   /* ROM 0x7488f4 */
static const char input_fn[] = "conversate_main_page_input_event_handler"; /* ROM 0x73d0e4 */

static const char up_top[] = "scroll_up_check blocked: current focus is top button"; /* ROM 0x71d148 */
static const char up_top_c[] = "[conversate.ui]scroll_up_check blocked: current focus is top button"; /* ROM 0x7013c0 */
static const char up_none[] = "scroll_up_check blocked: no list buttons"; /* ROM 0x73d08c */
static const char up_none_c[] = "[conversate.ui]scroll_up_check blocked: no list buttons"; /* ROM 0x71d180 */
static const char up_anim[] = "scroll_up_check blocked: list animation playing"; /* ROM 0x7327d4 */
static const char up_anim_c[] = "[conversate.ui]scroll_up_check blocked: list animation playing"; /* ROM 0x70a424 */
static const char down_none[] = "scroll_down_check blocked: no list buttons"; /* ROM 0x73d0b8 */
static const char down_none_c[] = "[conversate.ui]scroll_down_check blocked: no list buttons"; /* ROM 0x7136a8 */
static const char down_anim[] = "scroll_down_check blocked: list animation playing"; /* ROM 0x727e64 */
static const char down_anim_c[] = "[conversate.ui]scroll_down_check blocked: list animation playing"; /* ROM 0x701404 */
static const char down_cue[] = "scroll_down_check blocked: ai cue display disabled"; /* ROM 0x727e98 */
static const char down_cue_c[] = "[conversate.ui]scroll_down_check blocked: ai cue display disabled"; /* ROM 0x701448 */
static const char down_bottom[] =
    "scroll_down_check blocked: reached bottom, current_index=%d, button_count=%d"; /* ROM 0x6ec6b8 */
static const char down_bottom_c[] =
    "[conversate.ui]scroll_down_check blocked: reached bottom, current_index=%d, button_count=%d"; /* ROM 0x6dfd8c */

static const char in_anim[] = "main_input ignored while animating, code=%d"; /* ROM 0x73d110 */
static const char in_anim_c[] = "[conversate.ui]main_input ignored while animating, code=%d"; /* ROM 0x7136e4 */
static const char in_exit[] = "main_input unselected: double click -> app exit"; /* ROM 0x732804 */
static const char in_exit_c[] = "[conversate.ui]main_input unselected: double click -> app exit"; /* ROM 0x70a464 */
static const char in_top[] = "main_input unselected: select top button"; /* ROM 0x73d13c */
static const char in_top_c[] = "[conversate.ui]main_input unselected: select top button"; /* ROM 0x71d1b8 */
static const char in_cue[] = "AI cue display is disabled, skip main selected"; /* ROM 0x732834 */
static const char in_cue_c[] = "[conversate.ui]AI cue display is disabled, skip main selected"; /* ROM 0x70a4a4 */
static const char in_nolist[] = "No list container, skip main selected"; /* ROM 0x74891c */
static const char in_nolist_c[] = "[conversate.ui]No list container, skip main selected"; /* ROM 0x71d1f0 */
static const char in_first[] = "main_input unselected: select first list button"; /* ROM 0x732864 */
static const char in_first_c[] = "[conversate.ui]main_input unselected: select first list button"; /* ROM 0x70a4e4 */
static const char in_click[] = "main_input selected: click current_index=%d"; /* ROM 0x73d168 */
static const char in_click_c[] = "[conversate.ui]main_input selected: click current_index=%d"; /* ROM 0x713720 */
static const char in_unsel[] = "main_input selected: double click -> unselected"; /* ROM 0x732894 */
static const char in_unsel_c[] = "[conversate.ui]main_input selected: double click -> unselected"; /* ROM 0x70a524 */
static const char in_up[] = "main_input selected: scroll up result=%d"; /* ROM 0x73d194 */
static const char in_up_c[] = "[conversate.ui]main_input selected: scroll up result=%d"; /* ROM 0x71d228 */
static const char in_down[] = "main_input selected: scroll down result=%d"; /* ROM 0x73d1c0 */
static const char in_down_c[] = "[conversate.ui]main_input selected: scroll down result=%d"; /* ROM 0x71375c */

uint32_t conversate_list_scroll_up_value_get_5b23e4(void)
{
    g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;
    const uint32_t count = audio_conversate_ui_list_count_5b0c18();

    if (ui->top_button != NULL && ui->current_index == -1) {
        CONV_LOG0(3u, up_fn, 0x46u, 0x0c000000u, up_top, up_top_c);
        return 0u;
    }
    if (count == 0u) {
        CONV_LOG0(3u, up_fn, 0x4bu, 0x0c000000u, up_none, up_none_c);
        return 0u;
    }
    if (teleprompt_file_request_busy_5897e0() != 0u) {
        CONV_LOG0(3u, up_fn, 0x50u, 0x0c000000u, up_anim, up_anim_c);
        return 0u;
    }
    return 1u;
}

uint32_t conversate_list_scroll_down_value_get_5b24e8(void)
{
    g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;
    const int32_t count = (int32_t)audio_conversate_ui_list_count_5b0c18();

    if (count == 0) {
        CONV_LOG0(3u, down_fn, 0x5du, 0x0c000000u, down_none, down_none_c);
        return 0u;
    }
    if (teleprompt_file_request_busy_5897e0() != 0u) {
        CONV_LOG0(3u, down_fn, 0x64u, 0x0c000000u, down_anim, down_anim_c);
        return 0u;
    }
    if (ui->ai_cue_display == 0u) {
        CONV_LOG0(3u, down_fn, 0x69u, 0x0c000000u, down_cue, down_cue_c);
        return 0u;
    }
    if (ui->current_index < count - 1)
        return 1u;
    CONV_LOG(3u, down_fn, 0x6fu, 0x0c800000u, down_bottom, down_bottom_c, ui->current_index, count);
    return 0u;
}

/* Input handler of the idle Conversate states: double click closes the app page. */
void conversate_ui_idle_input_event_handler_5b2642(uint32_t code, const void *param)
{
    (void)param;
    if (code == CONV_INPUT_DOUBLE_CLICK)
        system_close_page_factory_0046ae9c(1u, 0x0b);
}

void conversate_main_page_input_event_handler_5b2652(uint32_t code, const void *param)
{
    g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;
    (void)param;

    if (ui->animating != 0u) {
        CONV_LOG(3u, input_fn, 0x85u, 0x0c400000u, in_anim, in_anim_c, code);
        return;
    }
    if (ui->selected == 0u) {
        if (code == CONV_INPUT_DOUBLE_CLICK) {
            CONV_LOG0(3u, input_fn, 0x8cu, 0x0c000000u, in_exit, in_exit_c);
            system_close_page_factory_0046ae9c(1u, 0x0b);
        } else if (ui->top_button != NULL) {
            CONV_LOG0(3u, input_fn, 0x90u, 0x0c000000u, in_top, in_top_c);
            audio_conversate_report_5b02e4(0x0cu, 0u);
        } else if (ui->ai_cue_display == 0u) {
            CONV_LOG0(2u, input_fn, 0x93u, 0x08000000u, in_cue, in_cue_c);
        } else if (audio_uart_lv_child_count_44ddea(ui->list) == 0u) {
            CONV_LOG0(2u, input_fn, 0x95u, 0x08000000u, in_nolist, in_nolist_c);
        } else {
            CONV_LOG0(3u, input_fn, 0x97u, 0x0c000000u, in_first, in_first_c);
            audio_conversate_report_5b02e4(0x0cu, 0u);
        }
        return;
    }

    conversate_timer_mgr_reset_select_timeout_5b3c70();
    if (code == CONV_INPUT_CLICK) {
        CONV_LOG(3u, input_fn, 0xa2u, 0x0c400000u, in_click, in_click_c, ui->current_index);
        audio_conversate_report_5b02e4(ui->current_index == -1 ? 6u : 8u, 0u);
    } else if (code == CONV_INPUT_DOUBLE_CLICK) {
        CONV_LOG0(3u, input_fn, 0xa9u, 0x0c000000u, in_unsel, in_unsel_c);
        audio_conversate_report_5b02e4(0x0du, 0u);
    } else if (code == CONV_INPUT_SCROLL_UP) {
        const uint32_t step = conversate_list_scroll_up_value_get_5b23e4();
        CONV_LOG(3u, input_fn, 0xadu, 0x0c400000u, in_up, in_up_c, step);
        if (step != 0u)
            audio_conversate_report_5b02e4(0x0eu, step);
    } else if (code == CONV_INPUT_SCROLL_DOWN) {
        const uint32_t step = conversate_list_scroll_down_value_get_5b24e8();
        CONV_LOG(3u, input_fn, 0xb3u, 0x0c400000u, in_down, in_down_c, step);
        if (step != 0u)
            audio_conversate_report_5b02e4(0x0fu, step);
    }
}
