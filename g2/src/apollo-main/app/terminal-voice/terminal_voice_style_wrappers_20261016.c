/* Voice page LVGL property wrappers and four-side margin composite. */
#include <stdint.h>
extern void audio_uart_page_style_apply_44be4c(void *,uint8_t,uint32_t,
                                                uint32_t);
extern void lv_obj_set_style_pad_left(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_right(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_top(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_bottom(void *,uint32_t,uint32_t);

void audio_terminal_ui_margins_5ebc5c(void *object,uint32_t value,
                                       uint32_t selector) {
    lv_obj_set_style_pad_left(object,value,selector);
    lv_obj_set_style_pad_right(object,value,selector);
    lv_obj_set_style_pad_top(object,value,selector);
    lv_obj_set_style_pad_bottom(object,value,selector);
}
