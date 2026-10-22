/* Conversate menu (reply list) page input, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate_ui_menu_page.c.
 * Native 0x5b5752..0x5b577b, 0x5b577c..0x5b57ab, 0x5b5886..0x5b58e7 and
 * 0x5b5d2c..0x5b5d5d (no strings; module from the neighbouring
 * conversate_ui_send_start_request 0x5b57ac and menu page create 0x5b59fa). */
#include <stdint.h>
#include <stddef.h>
#include "conversate_ui_context.h"

/* Reply list returned by 0x5b43e8: u16 count first. */
typedef struct {
    uint16_t count;
} g2_conversate_reply_list_t;

extern void *audio_conversate_reply_list_get_5b43e8(void);
extern uint8_t teleprompt_file_request_busy_5897e0(void); /* list animation playing */
extern void audio_conversate_report_5b02e4(uint32_t event, uint32_t value);
extern void audio_conversate_enter_loading_5b57ac(void); /* conversate_ui_send_start_request */
extern void system_close_page_factory_0046ae9c(uint32_t style, int32_t app_id);
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel); /* style pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel); /* style pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel); /* style pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel); /* style pad_right */

uint32_t conversate_menu_scroll_up_value_get_5b5752(const g2_conversate_ui_t *ui,
                                                    const g2_conversate_reply_list_t *replies)
{
    if (ui->current_index == -1 || replies == NULL || replies->count == 0u)
        return 0u;
    return teleprompt_file_request_busy_5897e0() == 0u ? 1u : 0u;
}

uint32_t conversate_menu_scroll_down_value_get_5b577c(const g2_conversate_ui_t *ui,
                                                      const g2_conversate_reply_list_t *replies)
{
    if (replies == NULL || replies->count == 0u)
        return 0u;
    if (teleprompt_file_request_busy_5897e0() == 0u &&
        ui->current_index < (int32_t)replies->count - 1)
        return 1u;
    return 0u;
}

void conversate_ui_menu_input_handler(uint32_t code, const void *param)
{
    const g2_conversate_reply_list_t *const replies = audio_conversate_reply_list_get_5b43e8();
    uint32_t step;
    (void)param;

    if (code == CONV_INPUT_DOUBLE_CLICK) {
        system_close_page_factory_0046ae9c(1u, 0x0b);
    } else if (code == CONV_INPUT_CLICK) {
        audio_conversate_enter_loading_5b57ac();
        audio_conversate_report_5b02e4(0x0cu, 0u);
    } else if (code == CONV_INPUT_SCROLL_UP) {
        step = conversate_menu_scroll_up_value_get_5b5752(G2_CONVERSATE_UI, replies);
        if (step != 0u)
            audio_conversate_report_5b02e4(0x0eu, step);
    } else if (code == CONV_INPUT_SCROLL_DOWN) {
        step = conversate_menu_scroll_down_value_get_5b577c(G2_CONVERSATE_UI, replies);
        if (step != 0u)
            audio_conversate_report_5b02e4(0x0fu, step);
    }
}

/* lv_obj_set_style_pad_all equivalent: left, right, top, bottom. */
void conversate_ui_menu_apply_base_style(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}
