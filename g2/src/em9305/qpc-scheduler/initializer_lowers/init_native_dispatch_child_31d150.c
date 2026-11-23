#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31d150..0x31d2ba: advance the periodic-advertising train
 * cursor (state block at (uintptr_t)&em9305_ram_8029ac: +0 subevent index, +1 slot, +4 count,
 * +7/+8 response filter, +12 time, +16 channel pointer, slot table at
 * +24) for the advertising set `set`. Each pass finds the next populated
 * subevent with 3173ac, records the 64-bit event position (interval +32
 * x factor +24, plus the slot when a channel is selected) at (uintptr_t)&em9305_ram_802a2c,
 * steps the time by +12 per skipped event, selects the next channel
 * (+56 entries, +176) and refreshes the subevent's TX power (30e6b0)
 * until a stop condition. When a channel was selected after at least one
 * full pass, the next anchor (+264 + time + +252, widened by 317ebc
 * against +248/+244) is scheduled with 302f4c and *done is set. Returns
 * 0 when the train is exhausted or filtered out, else 1. */
extern uint32_t opencfw_em9305_dispatch_child_3173ac(uintptr_t set, uintptr_t cursor);
extern uint32_t opencfw_em9305_dispatch_child_30e6b0(uintptr_t power);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_dispatch_child_302f4c(uint32_t start, uint32_t window, uintptr_t channel);

struct opencfw_em9305_train_cursor {
    uint32_t position;
    uint8_t count;
};

uint32_t opencfw_em9305_dispatch_child_31d150(uintptr_t set, uintptr_t done)
{
    const uintptr_t state=(uintptr_t)&em9305_ram_8029ac;
    volatile uint8_t *s8=(volatile uint8_t *)state;
    volatile uint32_t *s32=(volatile uint32_t *)state;
    volatile uint8_t *a=(volatile uint8_t *)set;
    uintptr_t no_channel=set+408u;
    int32_t passes=-1;
    uint32_t active=1u,base_time=0u;
    uintptr_t selected=0u;
    for(;;){
        uintptr_t previous=selected;
        if(s8[4]>a[25]){
            active=0u;
            break;
        }
        for(;;){
            if(opencfw_em9305_dispatch_child_3173ac(set,state)==0u){
                if(s8[7]==0u||a[274]==s8[8])active=0u;
                break;
            }
            if(*(volatile uint32_t *)(set+56u+s8[0]*4u)!=0u)break;
        }
        uint32_t factor=a[24];
        uint32_t high=*(volatile uint32_t *)(set+36u)*factor;
        uint64_t product=(uint64_t)*(volatile uint32_t *)(set+32u)*factor;
        selected=s32[4];
        product+=(uint64_t)high<<32;
        if(selected!=no_channel)product+=s8[1];
        em9305_ram_802a2c.u32_802a2c=(uint32_t)product;
        em9305_ram_802a2c.u32_802a30=(uint32_t)(product>>32);
        if(active==0u){
            selected=previous;
            break;
        }
        uint32_t steps=1u;
        if(s8[4]<a[25]){
            struct opencfw_em9305_train_cursor cursor;
            cursor.position=s32[0];
            cursor.count=s8[4];
            for(;;){
                if(opencfw_em9305_dispatch_child_3173ac(set,(uintptr_t)&cursor)==0u){
                    s32[4]=no_channel;
                    break;
                }
                uintptr_t channel=*(volatile uint32_t *)(set+56u+
                    *(volatile uint8_t *)&cursor.position*4u);
                if(channel!=0u){
                    s32[4]=channel+176u;
                    break;
                }
                ++steps;
            }
        }
        uint32_t interval=*(volatile uint32_t *)(set+12u);
        base_time=s32[3];
        uint32_t options=em9305_ram_805a6c.u8_805a86;
        s32[3]=interval*(uint8_t)steps+base_time;
        if((options&1u)!=0u)break;
        uint32_t index=s8[0];
        uintptr_t subevent=*(volatile uint32_t *)(set+56u+index*4u);
        if(subevent!=0u&&*(volatile uint8_t *)(subevent+101u)!=0u)break;
        uint32_t entry=*(volatile uint32_t *)(state+24u+index*24u+s8[1]*4u);
        if(entry==0u)break;
        if(index<a[52]&&subevent!=0u&&*(volatile uint8_t *)subevent!=0u){
            uint32_t power=opencfw_em9305_dispatch_child_30e6b0(subevent+120u);
            *(volatile uint8_t *)(subevent+177u)=(uint8_t)power;
            entry=*(volatile uint32_t *)(state+24u+s8[0]*24u+s8[1]*4u);
        }
        if(entry==0u)break;
        ++passes;
    }
    if(selected==0u||active==0u||passes<0)return active;
    uint32_t extra=*(volatile uint32_t *)(set+252u);
    uint32_t anchor=*(volatile uint32_t *)(set+264u);
    uint32_t reference=*(volatile uint32_t *)(set+248u);
    uint32_t window=*(volatile uint16_t *)(set+244u);
    anchor+=base_time+extra;
    uint32_t widening=opencfw_em9305_init_secondary_time_317ebc(anchor-reference,window);
    *(volatile uint32_t *)(set+172u)=widening<<1;
    (void)opencfw_em9305_dispatch_child_302f4c(anchor-widening,widening<<1,selected);
    *(volatile uint8_t *)done=1u;
    return active;
}
