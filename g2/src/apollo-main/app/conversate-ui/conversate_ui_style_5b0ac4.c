/* Native Conversate UI style wrapper 0x5b0ac4..0x5b0af5. */
#include <stdint.h>

extern void lv_obj_set_style_pad_left(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_pad_right(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_pad_top(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_pad_bottom(uint32_t, uint32_t, uint32_t);

void audio_conversate_ui_style_5b0ac4(uint32_t object, uint32_t value,
                                       uint32_t selector) {
    lv_obj_set_style_pad_left(object, value, selector);
    lv_obj_set_style_pad_right(object, value, selector);
    lv_obj_set_style_pad_top(object, value, selector);
    lv_obj_set_style_pad_bottom(object, value, selector);
}
