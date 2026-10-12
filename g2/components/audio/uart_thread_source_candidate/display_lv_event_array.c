/* Native LV event descriptor array count/slot/invalid accessors
 * 0x450388/0x450390/0x45037e over LV array 0x44ffcc/0x488578. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_array.c";
uint32_t audio_uart_lv_event_count_450388(void *list) {
    return *(uint32_t *)(void *)((uint8_t *)list+4u);
}
void *audio_uart_lv_event_slot_450390(void *list,uint32_t index) {
    uint8_t *a=(uint8_t *)list;
    uint32_t count=*(uint32_t *)(void *)(a+4u);
    if(index>=count)return 0;
    uint8_t *data=*(uint8_t **)(void *)a;
    if(data==0) {
        audio_uart_lvgl_log(3u,path,0xcau,"lv_array_at",
                            "Asserted at expression: %s (%s)","array->data != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint32_t stride=*(uint32_t *)(void *)(a+0x0cu);
    return data+index*stride;
}
uint32_t audio_uart_lv_event_descriptor_invalid_45037e(void *descriptor) {
    return (*(uint32_t *)(void *)((uint8_t *)descriptor+8u)>>16)&1u;
}
