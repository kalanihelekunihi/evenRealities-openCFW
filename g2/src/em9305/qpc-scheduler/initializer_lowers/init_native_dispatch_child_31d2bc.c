#include <stdint.h>

/* Native 0x31d2bc..0x31d438: advance the CIG event cursor (0x8029ac:
 * stream +0, subevent +1, flags +3/+7/+8, state pointer +0x10, anchor
 * +0xc, per-stream subevent table from +0x18, 24 bytes per stream). Each
 * round finds the next active stream with 317418, publishes the 64-bit
 * event counter (record +0x20/+0x24 times +0x18, plus the subevent unless
 * the cursor is on the group itself, +408) at 0x802a2c, looks ahead for
 * the following stream to advance the anchor by interval (+0x30) times
 * the streams skipped, and hops the stream's channel when it has a
 * pending subevent. After at least one full round with a valid stream
 * the receive timer is restarted (302f4c) and *done is set. Returns 0
 * when no stream remains. */
extern uint32_t opencfw_em9305_dispatch_child_317418(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_dispatch_child_30e6b0(uintptr_t);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_dispatch_child_302f4c(uint32_t,uint32_t,uint32_t);

static uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
static void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

uint32_t opencfw_em9305_dispatch_child_31d2bc(uintptr_t record,uintptr_t done)
{
    const uintptr_t cursor=(uintptr_t)0x8029acu;
    uintptr_t group=record+408u;
    int32_t round=-1;
    uint32_t ok=1u,current=0u,previous=0u,anchor_base=0u;
    for(;;) {
        previous=current;
        if(r8(cursor)>r8(record+52u)) {
            ok=0u;
            current=previous;
            break;
        }
        for(;;) {
            if(opencfw_em9305_dispatch_child_317418(record,cursor)==0u) {
                if(r8(cursor+7u)==0u||r8(cursor+8u)==r8(record+274u)) ok=0u;
                break;
            }
            if(r32(record+0x38u+4u*r8(cursor))!=0u&&r8(cursor+3u)==0u) break;
        }
        uint32_t multiplier=r8(record+0x18u);
        uint32_t high=r32(record+0x24u)*multiplier;
        uint64_t product=(uint64_t)r32(record+0x20u)*multiplier;
        uint32_t low=(uint32_t)product;
        high+=(uint32_t)(product>>32);
        current=r32(cursor+0x10u);
        if(current!=group) {
            uint32_t sum=low+r8(cursor+1u);
            high+=sum<low;
            low=sum;
        }
        w32(0x802a2cu,low);
        w32(0x802a30u,high);
        if(ok==0u) {
            current=previous;
            break;
        }
        uint32_t steps=1u;
        if(r8(cursor)<r8(record+52u)) {
            uint32_t probe_words[2];
            uint8_t *probe=(uint8_t *)probe_words;
            probe_words[0]=r32(cursor);
            probe[4]=(uint8_t)r8(cursor+4u);
            for(;;) {
                if(opencfw_em9305_dispatch_child_317418(record,(uintptr_t)probe)==0u) {
                    w32(cursor+0x10u,(uint32_t)group);
                    break;
                }
                uintptr_t stream=r32(record+0x38u+4u*probe[0]);
                if(stream!=0u&&probe[3]==0u) {
                    w32(cursor+0x10u,(uint32_t)stream+176u);
                    break;
                }
                ++steps;
            }
        }
        uint32_t interval=r32(record+0x30u);
        anchor_base=r32(cursor+0xcu);
        w32(cursor+0xcu,interval*(uint8_t)steps+anchor_base);
        if(r8(0x805a86u)&1u) break;
        uint32_t index=r8(cursor);
        uintptr_t stream=r32(record+0x38u+4u*index);
        if(stream!=0u&&r8(stream+101u)!=0u) break;
        uint32_t pending=r32(cursor+0x18u+(uint16_t)index*24u+r8(cursor+1u)*4u);
        if(pending==0u) break;
        if(index<r8(record+52u)&&stream!=0u&&r8(stream)!=0u) {
            w8(stream+177u,opencfw_em9305_dispatch_child_30e6b0(stream+120u));
            pending=r32(cursor+0x18u+(uint16_t)r8(cursor)*24u+r8(cursor+1u)*4u);
        }
        if(pending==0u) break;
        ++round;
    }
    if(current==0u||ok==0u||round<0) return ok;
    uint32_t anchor=r32(record+264u)+(anchor_base+r32(record+252u));
    uint32_t widening=opencfw_em9305_init_secondary_time_317ebc(anchor-r32(record+248u),
                                                                r16(record+244u));
    w32(record+172u,widening<<1);
    (void)opencfw_em9305_dispatch_child_302f4c(anchor-widening,widening<<1,current);
    w8(done,1u);
    return ok;
}
