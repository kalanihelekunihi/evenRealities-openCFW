/* Native hub_calibration_labels_update 0x4a7440..0x4a7472. */
#include <stdint.h>

extern void lv_obj_set_style_pad_left(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_pad_right(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_pad_top(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_pad_bottom(uint32_t, uint32_t, uint32_t);

void audio_uart_hub_calibration_labels_update_4a7440(uint32_t object,
                                                       uint32_t first,
                                                       uint32_t second) {
    lv_obj_set_style_pad_left(object, first, second);
    lv_obj_set_style_pad_right(object, first, second);
    lv_obj_set_style_pad_top(object, first, second);
    lv_obj_set_style_pad_bottom(object, first, second);
}
