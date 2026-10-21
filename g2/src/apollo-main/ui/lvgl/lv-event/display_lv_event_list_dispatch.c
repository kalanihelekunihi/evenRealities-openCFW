/* Native LVGL event-list dispatch 0x44ffe6. Snapshot/restore and post-send
 * compaction remain genuine child effects for callbacks that mutate the list. */
#include <stdint.h>
extern uint32_t audio_uart_lv_event_count_450388(void *);
extern void *audio_uart_lv_event_slot_450390(void *,uint32_t);
extern uint32_t audio_uart_lv_event_descriptor_invalid_45037e(void *);
extern void audio_uart_lv_event_restore_4502e0(void *);
extern void audio_uart_lv_event_compact_450346(void *);
static uint32_t rd32(const void *p){uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
uint32_t audio_uart_lv_event_list_dispatch_44ffe6(void *list,void *event,uint32_t phase) {
    if(list==0)return 1u;
    uint8_t *e=(uint8_t *)event;
    if((e[0x18u]&1u)!=0u)return 0u;
    uint32_t old_list[5];
    const uint32_t *snapshot=(const uint32_t *)list;
    old_list[0]=snapshot[0];old_list[1]=snapshot[1];old_list[2]=snapshot[2];
    old_list[3]=snapshot[3];old_list[4]=snapshot[4];
    uint8_t *l=(uint8_t *)list;
    uint8_t old_flag=l[0x14u];
    l[0x14u]=(uint8_t)(old_flag|1u);
    uint8_t result=1u;
    uint32_t count=audio_uart_lv_event_count_450388(list);
    for(uint32_t i=0;i<count;i++) {
        if((e[0x18u]&1u)!=0u)break;
        void *slot=audio_uart_lv_event_slot_450390(list,i);
        uint8_t *d=(uint8_t *)(uintptr_t)rd32(slot);
        uint32_t callback=rd32(d);
        if(callback==0u)continue;
        if(audio_uart_lv_event_descriptor_invalid_45037e(d)!=0u)continue;
        uint32_t filter=rd32(d+8u);
        if(((filter>>15)&1u)!=(uint8_t)phase)continue;
        uint32_t event_code=rd32(e+8u);
        if((filter&0xffff7fffu)!=0u && (filter&0xffff7fffu)!=event_code)continue;
        uint32_t user_data=rd32(d+4u);
        __builtin_memcpy(e+0x0cu,&user_data,4u);
        ((void (*)(void *))(uintptr_t)callback)(event);
        if((e[0x18u]&2u)!=0u)break;
        if((e[0x18u]&1u)!=0u){result=0u;break;}
    }
    if((old_flag&1u)!=0u)return result;
    if((e[0x18u]&1u)!=0u) {
        audio_uart_lv_event_restore_4502e0(old_list);
        return result;
    }
    l[0x14u]&=(uint8_t)~1u;
    audio_uart_lv_event_compact_450346(list);
    return result;
}
