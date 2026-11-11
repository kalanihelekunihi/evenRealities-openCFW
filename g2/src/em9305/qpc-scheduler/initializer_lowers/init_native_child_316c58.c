#include <stdint.h>

/* Native 0x316c58..0x316e5a: allocate a connection record. Take the first
 * free 912-byte record (byte 0 clear) of the config byte 34 records at
 * *0x805c70, clear it and load the link-layer defaults: feature masks
 * (0x805a84..0x805a98), handle-tagged procedure words, PHY 1M/257 octets
 * and the data length limits (config +0x26, 0x805ab4..), radio limits,
 * the task id 0x805b18, power/control defaults, the per-record allocation
 * hook (*0x805cd8 -> word 0), optional power-control state (+548 bit 1 and
 * 0x805a85 bit 7), the channel classification words and the command
 * counters. Returns the record, or 0 when none is free. The stock hook
 * call leaves the hook address in r1. */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_limit_317b10(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_command_count_30e4bc(void);
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t);

static uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
static void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

uintptr_t opencfw_em9305_child_316c58(void)
{
    uint32_t count=r8(r32(0x805cacu)+34u);
    if(count==0u) return 0u;
    uintptr_t base=r32(0x805c70u);
    uint32_t index=0u;
    uintptr_t rec;
    for(;;) {
        rec=base+index*912u;
        if(r8(rec)==0u) break;
        ++index;
        if(--count==0u) return 0u;
    }
    (void)opencfw_em9305_memset((void *)rec,0u,912u);
    uint32_t task=r8(0x805b18u);
    uint32_t features_low=r32(0x805a94u);
    uint32_t features_high=r32(0x805a98u);
    uint32_t local_low=r32(0x805a84u);
    uint32_t local_high=r32(0x805a88u);
    w16(rec+502u,0x5401u);
    w16(rec+482u,0x5301u);
    w16(rec+390u,0x4701u);
    w16(rec+734u,0x5101u);
    w16(rec+580u,328u);
    uint32_t octets=r16(r32(0x805cacu)+0x26u);
    w16(rec+576u,328u);
    w32(rec+8u,local_high);
    if((int32_t)octets>251) octets=251u;
    uint32_t rx_octets=r16(0x805ab6u);
    uint32_t rx_time=r16(0x805ab8u);
    w16(rec+566u,octets);
    w16(rec+568u,(octets<<6)+976u);
    w8(rec,1u);
    w16(rec+388u,index);
    w16(rec+480u,index);
    w16(rec+500u,index);
    w16(rec+732u,index);
    w16(rec+578u,27u);
    w16(rec+574u,27u);
    w32(rec+4u,local_low);
    w32(rec+548u,features_high);
    w32(rec+544u,features_low);
    w32(rec+540u,features_high);
    w32(rec+536u,features_low);
    w8(rec+396u,task);
    w8(rec+740u,task);
    w8(rec+488u,task);
    w8(rec+508u,task);
    w16(rec+570u,rx_octets);
    w16(rec+572u,rx_time);
    w16(rec+76u,257u);
    w16(rec+592u,opencfw_em9305_radio_limit_317b10(rec,rec+574u));
    uint32_t limit=opencfw_em9305_radio_limit_317b10(rec,rec+566u);
    uint32_t map_high=r32(0x805accu);
    uint32_t map_count=r16(0x805ac8u);
    uint32_t value_b=r8(0x805acbu);
    uint32_t value_aa8=r8(0x805aa8u);
    uint32_t value_a=r8(0x805acau);
    w16(rec+590u,limit);
    w8(rec+598u,2u);
    w8(rec+599u,2u);
    w8(rec+600u,2u);
    w16(rec+594u,map_count);
    w32(rec+616u,map_high);
    uintptr_t hooks=r32(0x805cd8u);
    w8(rec+402u,6u);
    w8(rec+596u,value_a);
    w8(rec+746u,value_aa8);
    w8(rec+614u,value_b);
    if(hooks!=0u) {
        uintptr_t hook=r32(hooks);
        if(hook!=0u) ((void (*)(uint32_t,uintptr_t))hook)((uint16_t)index,hook);
    }
    if((r8(rec+548u)&2u)&&(r8(0x805a85u)&0x80u)) {
        uintptr_t power=base+index*912u;
        w8(power+778u,r8(r32(0x805cacu)+66u));
        uint32_t step=r8(r32(0x805cacu)+67u);
        w32(power+824u,0u);
        w8(power+770u,1u);
        w8(power+769u,0u);
        w8(power+833u,0u);
        w16(power+822u,0u);
        w8(power+564u,0xffu);
        w8(power+563u,0xffu);
        w8(power+562u,0xffu);
        w8(power+561u,0xffu);
        w16(power+776u,0u);
        w32(power+784u,0u);
        w8(power+793u,0u);
        w16(power+780u,0u);
        w8(power+779u,step);
    }
    uintptr_t entry=base+index*912u;
    w32(entry+836u,r32(0x805ad0u));
    w32(entry+840u,r32(0x805ad4u));
    uint32_t instant=r16(0x805ad8u);
    w16(entry+846u,1u);
    w16(entry+844u,instant);
    (void)opencfw_em9305_command_count_30e4bc();
    w8(0x805a70u,r8(0x805a70u)+1u);
    (void)opencfw_em9305_common_request_30455c(1u);
    return r32(0x805c70u)+index*912u;
}
