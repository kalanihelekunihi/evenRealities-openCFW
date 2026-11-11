/* Apollo session selector leaf helpers, stock 0x5eca00 and 0x5ecc74. */
#include <stdint.h>

extern void lv_obj_set_style_pad_left(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_right(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_top(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_bottom(void *,uint32_t,uint32_t);
extern int32_t g2_audio_dump_snprintf(char *,uint32_t,const char *,...);

void audio_terminal_session_four_margins_5eca00(void *object,uint32_t value,
                                                uint32_t selector) {
    lv_obj_set_style_pad_left(object,value,selector);
    lv_obj_set_style_pad_right(object,value,selector);
    lv_obj_set_style_pad_top(object,value,selector);
    lv_obj_set_style_pad_bottom(object,value,selector);
}

void audio_terminal_session_row_text_5ecc74(char *destination,uint32_t capacity,
                                            const uint8_t *source) {
    if (destination==0 || capacity==0u) return;
    destination[0]=0;
    if (source==0) return;
    uint32_t length=(uint32_t)source[4]|((uint32_t)source[5]<<8);
    if (length>=capacity) length=capacity-1u;
    for (uint32_t i=0;i<length;++i) destination[i]=(char)source[6u+i];
    destination[length]=0;
    if (length==0u) {
        uint32_t id=(uint32_t)source[0]|((uint32_t)source[1]<<8)|
                    ((uint32_t)source[2]<<16)|((uint32_t)source[3]<<24);
        (void)g2_audio_dump_snprintf(destination,capacity,"Session %lu",id);
    }
}
