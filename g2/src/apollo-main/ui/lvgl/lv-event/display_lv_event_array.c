/* Native LV event descriptor array count/slot/invalid accessors
 * 0x450388/0x450390/0x45037e over LV array 0x44ffcc/0x488578. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_array.c";
uint32_t audio_uart_lv_event_descriptor_invalid_45037e(void *descriptor) {
    return (*(uint32_t *)(void *)((uint8_t *)descriptor+8u)>>16)&1u;
}
