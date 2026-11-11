#include <stdint.h>
#include <stddef.h>
extern void *r1_native_memory_move(void *,const void *,size_t);
extern uint32_t r1_gomore_sleep_interval_build_native(volatile void *,uint32_t,uint32_t,uint32_t,uint32_t,volatile void *,volatile void *,uint32_t,uint32_t);
extern uint32_t r1_gomore_sleep_interval_refine_native(volatile void *,uint32_t,uint32_t,volatile void *,uint32_t,uint32_t,uint32_t);
struct __attribute__((packed,may_alias)) compose_word { uint32_t value; };
uint32_t r1_gomore_sleep_interval_compose_native(volatile void *output,
        uint32_t context,uint32_t stored,uint32_t timezone,uint32_t mode,
        volatile void *controls,volatile void *source,uint32_t aggregation,uint32_t policy)
{
    _Alignas(8) volatile uint8_t work[32];
    _Alignas(8) volatile uint8_t snapshot[32];
    (void)r1_gomore_sleep_interval_build_native(work,context,mode,stored,timezone,controls,source,aggregation,policy);
    r1_native_memory_move((void *)snapshot,(const void *)work,32);
    uint32_t metadata16=((volatile struct compose_word *)(snapshot+16))->value;
    uint32_t metadata20=((volatile struct compose_word *)(snapshot+20))->value;
    (void)r1_gomore_sleep_interval_refine_native(work,context,stored,snapshot,aggregation,policy,timezone);
    r1_native_memory_move((void *)snapshot,(const void *)work,32);
    ((volatile struct compose_word *)(snapshot+16))->value=metadata16;
    ((volatile struct compose_word *)(snapshot+20))->value=metadata20;
    uint32_t start=((volatile struct compose_word *)snapshot)->value;
    uint32_t end=((volatile struct compose_word *)(snapshot+4))->value;
    uint32_t rounded=((end-start)/30u)*30u;
    uint32_t fresh_start=((volatile struct compose_word *)snapshot)->value;
    ((volatile struct compose_word *)(snapshot+4))->value=fresh_start+rounded;
    return (uint32_t)(uintptr_t)r1_native_memory_move((void *)output,(const void *)snapshot,32);
}
