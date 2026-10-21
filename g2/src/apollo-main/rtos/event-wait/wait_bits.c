/* Event-group wait worker, stock 0x47ebf8, from pinned FreeRTOS 10.5.1. */
#include <stdint.h>
#include <stddef.h>
extern uint32_t audio_scheduler_state(void); /* stock 0x4558a4 */
extern void audio_suspend(void);
extern int32_t stock_scheduler_resume(void);
extern void audio_yield(void);
extern void stock_enter_critical(void);
extern void stock_exit_critical(void);
extern void g2_event_place_unordered(void *list,uint32_t value,uint32_t ticks);
extern uint32_t g2_event_reset_item_value(void);
extern void g2_event_wait_assert(void) __attribute__((noreturn));
static int condition(uint32_t current,uint32_t request,uint32_t all) {
    return all ? ((current&request)==request) : ((current&request)!=0u);
}
uint32_t g2_event_wait_bits(uint32_t handle,uint32_t request,uint32_t clear,
                            uint32_t all,uint32_t ticks) {
    void *group=(void *)(uintptr_t)handle;
    if(!group || !request || (request&0xff000000u) ||
       (audio_scheduler_state()==0u && ticks!=0u))
        g2_event_wait_assert();
    volatile uint32_t *bits=(volatile uint32_t *)group;
    audio_suspend();
    uint32_t result=*bits;
    uint32_t wait_ticks=ticks;
    if(condition(result,request,all)) {
        wait_ticks=0u;
        if(clear) *bits=result&~request;
    } else if(ticks==0u) {
        wait_ticks=0u;
    } else {
        uint32_t control=request|(clear?0x01000000u:0u)|
                         (all?0x04000000u:0u);
        g2_event_place_unordered((uint8_t *)group+4u,control,ticks);
        result=0u;
    }
    int32_t yielded=stock_scheduler_resume();
    if(wait_ticks!=0u) {
        if(yielded==0) audio_yield();
        result=g2_event_reset_item_value();
        if((result&0x02000000u)==0u) {
            stock_enter_critical();
            result=*bits;
            if(condition(result,request,all) && clear) *bits=result&~request;
            stock_exit_critical();
        }
        result&=~0xff000000u;
    }
    return result;
}
