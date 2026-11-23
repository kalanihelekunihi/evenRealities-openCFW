#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32c990..0x32ca20: apply the pending connection-parameter
 * request at ((uintptr_t)&em9305_ram_8027e0 + 0x3cu) to the record. Skipped (returning the options byte)
 * when bit 4 of the record options (+4) is set or the request fails
 * validation. Otherwise the 24-byte request is copied to +684; with
 * option bit 5 the first three request words replace words 165..167,
 * else the interval range at +660/+662 takes each new bound that lies
 * within it and the range at +664/+666 widens to the new limits. Returns
 * the last stored value, as in stock. */
extern uint32_t opencfw_em9305_ll_connection_parameters_validate_30a6b4(uintptr_t controls);
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);

static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}

uint32_t opencfw_em9305_child_32c990(uintptr_t record)
{
    uint32_t request[3];
    uint32_t options=*(volatile uint8_t *)(record+4u);
    request[2]=0u;
    request[0]=*(volatile uint32_t *)((uintptr_t)&em9305_ram_8027e0 + 0x3cu);
    request[1]=*(volatile uint32_t *)((uintptr_t)&em9305_ram_8027e0 + 0x40u);
    if((options&0x10u)!=0u)return options;
    uint32_t status=opencfw_em9305_ll_connection_parameters_validate_30a6b4(
        (uintptr_t)request);
    if(status!=0u)return status;
    (void)opencfw_em9305_memcpy((void *)(record+684u),(const void *)((uintptr_t)&em9305_ram_8027e0 + 0x3cu),24u);
    if((*(volatile uint8_t *)(record+4u)&0x20u)!=0u){
        uint32_t first=request[0],second=request[1],third=request[2];
        *(volatile uint32_t *)(record+660u)=first;
        *(volatile uint32_t *)(record+664u)=second;
        *(volatile uint32_t *)(record+668u)=third;
        return third;
    }
    uintptr_t range=record+660u;
    uint32_t minimum=r16(((uintptr_t)&em9305_ram_8027e0 + 0x3cu));
    uint32_t low=r16(range);
    if(minimum>=low&&r16(range+2u)>=minimum){
        low=minimum;
        w16(range,minimum);
    }
    uint32_t maximum=r16(((uintptr_t)&em9305_ram_8027e0 + 0x3eu));
    if(maximum>=low&&r16(range+2u)>=maximum)w16(range+2u,maximum);
    uintptr_t limits=record+664u;
    uint32_t new_low=r16(((uintptr_t)&em9305_ram_8027e0 + 0x40u)),new_high=r16(((uintptr_t)&em9305_ram_8027e0 + 0x42u));
    uint32_t old_low=r16(limits),old_high=r16(limits+2u);
    uint32_t lowest=old_low<new_low?old_low:new_low;
    uint32_t highest=old_high>new_high?old_high:new_high;
    w16(limits,lowest);
    w16(limits+2u,highest);
    return highest;
}
