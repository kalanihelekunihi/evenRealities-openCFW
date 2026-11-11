/* Stock 0x8a068. Preserve native R0 forwarding through an explicit logging
 * tail boundary: the linked SDK void interface does not promise that value. */
#include <stdint.h>
#include <stddef.h>
#include "../board/native_watchdog.h"
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern uint32_t r1_stream_sample_rate_copy(const void *,uint32_t,uint32_t,void *,uint32_t,uint32_t);
extern uint32_t r1_stream_timer_period_set(volatile uint32_t *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
/* The SDK declares this entry void. Its native ARM return leaves R0 from
 * std_n, and the stock reducer forwards that register value. This local
 * declaration models that raw ABI result; the musttail call preserves the
 * caller's LR, SP and all four argument registers. */
extern uint32_t nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
__attribute__((noinline))
uint32_t r1_stream_rate_reduce_log_tail_result(
 uint32_t metadata,const char *format,uint32_t owner,uint32_t ticks)
{
 __attribute__((musttail)) return
     nrf_log_frontend_std_2(metadata,format,owner,ticks);
}
extern uint32_t r1_stream_zero_divisor_result(void);
extern _Noreturn void r1_bae8_rx_allocation_fault(void);
static inline uint32_t period(uint32_t rate)
{return rate?1024u/rate:r1_stream_zero_divisor_result();}
uint32_t r1_stream_object_rate_reduce(void *owner)
{
    volatile uint8_t *object=owner;
    if(!object)return 0;
    struct r1_native_list *list=(struct r1_native_list *)(uintptr_t)(object+44);
    uint32_t maximum=0;
    for(volatile uint8_t *node=r1_native_list_head(list);node;node=r1_native_list_next(list,(void *)(uintptr_t)node)){
        uint32_t rate=node[13];
        if(rate>maximum)maximum=rate;
    }
    if(!maximum)return 0;
    uint32_t current=object[16];
    if(current<=maximum)return current;
    if(((volatile uint32_t *)object)[5]){
        uint32_t width=*(volatile uint16_t *)(object+28);
        void *buffer=pvPortMalloc(maximum*width*2u);
        if(!buffer)r1_bae8_rx_allocation_fault();
        width=*(volatile uint16_t *)(object+28);
        uint32_t old=((volatile uint32_t *)object)[5];
        uint32_t used=((volatile uint32_t *)object)[6];
        uint32_t rate=object[16];
        uint32_t count=r1_stream_sample_rate_copy((const void *)(uintptr_t)old,rate,used,buffer,maximum,width);
        vPortFree((void *)(uintptr_t)((volatile uint32_t *)object)[5]);
        ((volatile uint32_t *)object)[5]=(uint32_t)(uintptr_t)buffer;
        ((volatile uint32_t *)object)[6]=count;
    }
    uint32_t ticks=1024u/maximum;
    object[16]=(uint8_t)maximum;
    (void)r1_stream_timer_period_set((volatile uint32_t *)(uintptr_t)((volatile uint32_t *)object)[8],ticks);
    if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
        ticks=period(object[16]);
        (void)r1_structured_log_format(0x0c800000,"[RING]reset timer,%s, tick:%d","[RING]reset timer,%s, tick:%d",owner,ticks);
    }
    uint32_t mode=r1_structured_log_mode_get();
    if(mode&2u){
        ticks=period(object[16]);
        return r1_stream_rate_reduce_log_tail_result(0x001c0003,"reset timer,%s, tick:%d",(uint32_t)(uintptr_t)owner,ticks);
    }
    /* Stock's final LSLS uses R0 itself, including on the no-log return. */
    return mode<<30;
}
