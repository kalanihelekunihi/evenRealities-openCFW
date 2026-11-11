/* Native LV style setters and page manager composite 0x44120e..0x4413b0,
 * 0x44146a and 0x45ec7c. Return R7 is unused by authenticated callers. */
#include <stdint.h>
/* The setters 0x44120e..0x4413b0 and 0x44146a are upstream LVGL
 * lv_obj_set_style_{pad_top,pad_bottom,pad_left,pad_right,border_width,
 * outline_width,outline_pad,shadow_width,shadow_offset_x,shadow_offset_y,
 * shadow_spread,radius} (lv_obj_style_gen.c); callers use those directly. */
extern void lv_obj_set_style_pad_top(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_bottom(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_left(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_right(void *,uint32_t,uint32_t);
void audio_uart_page_45ec7c(void *object,uint32_t value,uint32_t selector) {
    lv_obj_set_style_pad_left(object,value,selector);
    lv_obj_set_style_pad_right(object,value,selector);
    lv_obj_set_style_pad_top(object,value,selector);
    lv_obj_set_style_pad_bottom(object,value,selector);
}
