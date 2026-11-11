/* Native call target 0x4d2b9c, inside decompiler envelope 0x4d2b9a. */
#include <stdint.h>
extern void lv_obj_set_style_pad_left(uint32_t,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_right(uint32_t,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_top(uint32_t,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_bottom(uint32_t,uint32_t,uint32_t);

/* Stock 0x4D2B9A (system-alert page style; TSV row starts at the 2-byte pad before 0x4d2b9c) */
void audio_system_alert_page_style_4d2b9c(uint32_t object,uint32_t value,
                                           uint32_t selector) {
    lv_obj_set_style_pad_left(object,value,selector);
    lv_obj_set_style_pad_right(object,value,selector);
    lv_obj_set_style_pad_top(object,value,selector);
    lv_obj_set_style_pad_bottom(object,value,selector);
}
