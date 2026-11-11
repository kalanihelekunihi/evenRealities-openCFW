/* Stock 0x89890 registration and 0x8a5d0 timer-period store. Architectural
 * zero-divisor behavior remains explicit rather than invoking undefined C. */
#include <stdint.h>
#include <stddef.h>
#include "../board/native_watchdog.h"
extern uint32_t r1_native_list_empty(struct r1_native_list *);
extern void *r1_native_list_prepend(struct r1_native_list *);
extern size_t strlen(const char *);
extern void *r1_native_memory_move(void *,const void *,size_t),*pvPortMalloc(size_t);
extern void vPortFree(void *);
extern uint32_t r1_stream_sample_rate_copy(const void *,uint32_t,uint32_t,void *,uint32_t,uint32_t);
extern uint32_t r1_stream_timer_create_front(uint32_t,uint32_t,uint32_t),r1_stream_timer_create_back(uint32_t,uint32_t,uint32_t);
extern void r1_stream_timer_dispatch(void *timer);
extern uint32_t r1_stream_zero_divisor_result(void);
extern _Noreturn void r1_bae8_rx_allocation_fault(void);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
typedef struct __attribute__((packed,may_alias)) {uint32_t value;} word_t;
typedef struct __attribute__((packed,may_alias)) {uint16_t value;} half_t;
static inline uint32_t rd(const volatile uint8_t *p){return ((const volatile word_t *)p)->value;}
static inline void wr(volatile uint8_t *p,uint32_t v){((volatile word_t *)p)->value=v;}
static inline uint32_t rh(const volatile uint8_t *p){return ((const volatile half_t *)p)->value;}
static inline void wh(volatile uint8_t *p,uint16_t v){((volatile half_t *)p)->value=v;}
static inline uint32_t period(uint32_t divisor){return divisor?1024u/divisor:r1_stream_zero_divisor_result();}
#define LOG0(tag,sdk_tag,ring,sdk) do { \
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) (void)r1_structured_log_format(tag,ring,ring); \
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(sdk_tag,sdk); \
}while(0)
uint32_t r1_stream_timer_period_set(volatile uint32_t *timer,uint32_t value)
{
    if (!timer) r1_bae8_rx_allocation_fault();
    *timer=value;
    return (uint32_t)(uintptr_t)timer;
}
uint32_t r1_sensor_stream_register_object(void *object,const char *group,uintptr_t callback,uint32_t order,uint32_t flags)
{
    if (!object || !group) r1_bae8_rx_allocation_fault();
    volatile uint8_t *o=object;
    struct r1_native_list *list=(struct r1_native_list *)((uintptr_t)object+44u);
    uint32_t empty=r1_native_list_empty(list);
    volatile uint8_t *record=r1_native_list_prepend(list);
    if (!record) {
        LOG0(0x04000000,0x001c0001,"[RING]lisent register fail","lisent register fail");
        return 0;
    }
    if (order>1) {
        LOG0(0x0c000000,0x001c0003,"[RING]only support 1 ord","only support 1 ord");
        order=1;
    }
    uint32_t length=(uint8_t)strlen(group);
    if (length>8) length=8;
    wr(record+16,(uint32_t)callback);
    record[13]=(uint8_t)order;record[14]=(uint8_t)flags;wh(record+20,0);
    (void)r1_native_memory_move((void *)(record+4),group,length);
    wr(record,(uint32_t)(uintptr_t)object);
    if (empty) {
        o[16]=(uint8_t)order;
        uint32_t buffer=(uint32_t)(uintptr_t)pvPortMalloc(order*rh(o+28)*2u);
        wr(o+20,buffer);
        if (!buffer) r1_bae8_rx_allocation_fault();
        uint32_t ops=rd(o+12),context=rd(o+36);
        if (ops) {
            uint32_t start=rd((const volatile uint8_t *)(uintptr_t)ops);
            if (start) ((void (*)(uint32_t))(uintptr_t)start)(context);
        }
        uint32_t divisor=o[16],mode=o[40];
        uint32_t ticks=period(divisor);
        uint32_t timer=(mode&1u)?r1_stream_timer_create_back((uint32_t)(uintptr_t)r1_stream_timer_dispatch,ticks,(uint32_t)(uintptr_t)object):r1_stream_timer_create_front((uint32_t)(uintptr_t)r1_stream_timer_dispatch,ticks,(uint32_t)(uintptr_t)object);
        wr(o+32,timer);
    } else if (o[16]<order) {
        if (rd(o+20)) {
            void *buffer=pvPortMalloc(order*rh(o+28)*2u);
            if (!buffer) r1_bae8_rx_allocation_fault();
            uint32_t width=rh(o+28),old=rd(o+20),used=rd(o+24),rate=o[16];
            uint32_t count=r1_stream_sample_rate_copy((const void *)(uintptr_t)old,rate,used,buffer,order,width);
            vPortFree((void *)(uintptr_t)rd(o+20));
            wr(o+20,(uint32_t)(uintptr_t)buffer);wr(o+24,count);
        }
        uint32_t ticks=period(order);
        o[16]=(uint8_t)order;
        (void)r1_stream_timer_period_set((volatile uint32_t *)(uintptr_t)rd(o+32),ticks);
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
            uint32_t tick=period(o[16]);
            (void)r1_structured_log_format(0x0c800000,"[RING]reset timer,%s, tick:%d","[RING]reset timer,%s, tick:%d",object,tick);
        }
        if (r1_structured_log_mode_get()&2u) {
            uint32_t tick=period(o[16]);
            nrf_log_frontend_std_2(0x001c0003,"reset timer,%s, tick:%d",(uint32_t)(uintptr_t)object,tick);
        }
    }
    return (uint32_t)(uintptr_t)record;
}
