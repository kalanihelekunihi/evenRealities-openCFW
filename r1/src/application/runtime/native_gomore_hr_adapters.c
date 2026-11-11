#include <stdint.h>
#include <stddef.h>
#include "native_gomore_authorization.h"
extern uint32_t r1_gomore_authorization_dispatch_native(uint32_t,uint32_t);
extern void *r1_native_memory_move(void *,const void *,size_t);
uint32_t r1_gomore_hr_topic_adapter(uint32_t context,volatile void *payload,uint32_t length)
{
    (void)length;
    if (!payload) return context;
    uint32_t sample=*(const volatile uint8_t *)payload;
    union {float value;uint32_t bits;} converted={.value=(float)sample};
    r1_gomore_authorization_samples.hr_value=converted.bits;
    r1_gomore_authorization_state.padding0[0]|=4u;
    if (r1_gomore_authorization_state.entries[5].flags&1u)
        return r1_gomore_authorization_dispatch_native(5,0);
    return 0;
}
uint32_t r1_gomore_hrv_topic_adapter(uint32_t context,volatile void *payload,uint32_t length)
{
    (void)length;
    if (!payload) return context;
    uint32_t data=(uint32_t)(uintptr_t)payload;
    uint32_t count=*(volatile uint8_t *)(uintptr_t)(data+9u);
    if (count>4) {
        count=4;
        *(volatile uint8_t *)(uintptr_t)(data+9u)=4;
    }
    r1_gomore_authorization_samples.hrv_active=(uint8_t)count;
    r1_gomore_authorization_state.hrv_count=0;
    r1_gomore_authorization_state.hrv_total=0;
    count=*(volatile uint8_t *)(uintptr_t)(data+9u);
    return (uint32_t)(uintptr_t)r1_native_memory_move(
        (void *)(uintptr_t)&r1_gomore_authorization_state.hrv_count,
        (const void *)(uintptr_t)data,count*2u);
}
