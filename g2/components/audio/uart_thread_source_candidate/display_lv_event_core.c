/* Native LVGL event_send_core 0x451a6c. The pinned LVGL 9.3 source matches
 * its preprocess/base/normal dispatch and recursive parent bubbling flow. */
#include <stdint.h>
extern void *audio_uart_lv_active_input_452ef8(void);
extern uint32_t audio_uart_lv_event_list_dispatch_44ffe6(void *,void *,uint32_t);
extern uint32_t audio_uart_lv_object_event_base_4516f8(void *,void *);
extern void *audio_uart_lv_obj_has_parent_44dca2(void *); /* selected exact body */
extern uint32_t audio_uart_lv_event_is_bubbled_451b34(void *);

uint32_t audio_uart_lv_event_core_451a6c(void *event) {
    uint8_t *e=(uint8_t *)event;
    if(audio_uart_lv_active_input_452ef8()!=0) {
        if((e[0x18u]&2u)!=0u)return 1u;
        if((e[0x18u]&1u)!=0u)return 0u;
    }
    uint8_t *target=*(uint8_t **)(void *)e;
    uint8_t *spec=*(uint8_t **)(void *)(target+8u);
    void *list=spec!=0?(void *)(spec+8u):0;
    uint32_t result=(uint8_t)audio_uart_lv_event_list_dispatch_44ffe6(list,event,1u);
    if((uint8_t)result!=1u || (e[0x18u]&2u)!=0u)return (uint8_t)result;
    result=(uint8_t)audio_uart_lv_object_event_base_4516f8(0,event);
    if((uint8_t)result!=1u || (e[0x18u]&2u)!=0u)return (uint8_t)result;
    result=(uint8_t)audio_uart_lv_event_list_dispatch_44ffe6(list,event,0u);
    if((uint8_t)result!=1u || (e[0x18u]&2u)!=0u)return (uint8_t)result;
    void *parent=audio_uart_lv_obj_has_parent_44dca2(*(void **)(void *)e);
    if(parent!=0 && audio_uart_lv_event_is_bubbled_451b34(event)!=0u) {
        *(void **)(void *)e=parent;
        result=(uint8_t)audio_uart_lv_event_core_451a6c(event);
    }
    return (uint8_t)result;
}
