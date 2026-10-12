/* Native lv_display_send_event 0x44fdbe: zeroed 28-byte event envelope,
 * capture then bubble phase through the authentic LV event-list dispatcher. */
#include <stdint.h>
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_event_list_dispatch_44ffe6(void *,void *,uint32_t);
uint32_t audio_uart_lv_display_event_44fdbe(void *display,uint32_t code,void *parameter) {
    uint8_t event[0x1cu];
    audio_uart_buffer_zero(event,0x1cu,0u);
    __builtin_memcpy(event,&display,4u);
    __builtin_memcpy(event+4u,&display,4u);
    __builtin_memcpy(event+8u,&code,4u);
    __builtin_memcpy(event+0x10u,&parameter,4u);
    uint8_t *list=(uint8_t *)display+0x2e4u;
    uint8_t result=(uint8_t)audio_uart_lv_event_list_dispatch_44ffe6(list,event,1u);
    if(result==1u)
        result=(uint8_t)audio_uart_lv_event_list_dispatch_44ffe6(list,event,0u);
    return result;
}
