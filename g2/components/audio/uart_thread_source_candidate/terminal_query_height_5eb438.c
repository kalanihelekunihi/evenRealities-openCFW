/* Query content-height helper and two style metrics, stock 0x5eb2a8/0x5eb2b2/0x5eb438. */
#include <stdint.h>

extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);

uint32_t audio_terminal_query_style_16_5eb2a8(void *object,uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object,selector,16u);
}
uint32_t audio_terminal_query_style_17_5eb2b2(void *object,uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object,selector,17u);
}
int32_t audio_terminal_query_height_5eb438(uint8_t *state) {
    if (state==0) return 0;
    uint32_t root=(uint32_t)state[0x214u]|((uint32_t)state[0x215u]<<8)|
                  ((uint32_t)state[0x216u]<<16)|((uint32_t)state[0x217u]<<24);
    if (root==0u) return 0;
    int32_t height=audio_uart_lv_obj_height_43fdda((void *)(uintptr_t)root);
    int32_t top=(int32_t)audio_terminal_query_style_16_5eb2a8((void *)(uintptr_t)root,0u);
    int32_t bottom=(int32_t)audio_terminal_query_style_17_5eb2b2((void *)(uintptr_t)root,0u);
    int32_t inner=height-top-bottom;
    return inner>=1 ? inner : height;
}
