/* Query four-side spacing wrapper, stock 0x5eb2bc..0x5eb2ed. */
#include <stdint.h>
extern void lv_obj_set_style_pad_left(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_right(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_top(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_bottom(void *,uint32_t,uint32_t);

void audio_terminal_query_four_margins_5eb2bc(void *object,uint32_t value,
                                              uint32_t selector) {
    lv_obj_set_style_pad_left(object,value,selector);
    lv_obj_set_style_pad_right(object,value,selector);
    lv_obj_set_style_pad_top(object,value,selector);
    lv_obj_set_style_pad_bottom(object,value,selector);
}
