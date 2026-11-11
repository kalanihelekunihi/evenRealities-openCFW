#include <stdint.h>

/* Native 0x3282c4..0x32841c: initialise the record's 312-byte connection
 * setup block (+2468) for an advertiser start (as 32841c, with role 2) and
 * its connection request block (+2524): access address 0x8e89bed6, CRC
 * init 0x555555, clock accuracy (+60, or 0x805a9c when 0x7f), channel map
 * (+63), PHY code for PHY index +69 (1,2,1,2 for 1..4), a 0x20 window at
 * +2592 (and at +2594 for legacy connectable events with bit 1 of +59),
 * the advertising PDU (+945, built by 3239fc from +1420) and scan
 * response (+1011, 323b10) descriptors, and a 40-byte event buffer for
 * the 32bc98 completion (failure: status 31 at +826 and 325a40 reason 4).
 * Hands the block to 328270. */
extern void *opencfw_em9305_memset(void *dst,uint32_t value,uint32_t count);
extern void opencfw_em9305_child_3280e8(uintptr_t object);
extern uint32_t opencfw_em9305_child_3239fc(uintptr_t,uintptr_t,uintptr_t,uint32_t);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t length);
extern uint32_t opencfw_em9305_child_32bc98(uintptr_t owner,uintptr_t pdu);
extern uint32_t opencfw_em9305_child_325a40(uintptr_t record,uint32_t status);
extern uint32_t opencfw_em9305_child_323b10(uintptr_t set,uintptr_t output,
                                            uint32_t count);
extern uint32_t opencfw_em9305_child_328270(uintptr_t record,uintptr_t object);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

uint32_t opencfw_em9305_child_3282c4(uintptr_t record)
{
    uintptr_t setup=record+0x9a4u;
    (void)opencfw_em9305_memset((void *)setup,0u,312u);
    int32_t accuracy=*(volatile int8_t *)(record+60u);
    uint32_t phy=r8(record+0xae0u);
    uint32_t done=(uint32_t)(uintptr_t)opencfw_em9305_child_3280e8;
    w8(setup+26u,1u);
    w8(setup+24u,2u);
    w8(setup+48u,7u);
    w32(setup+36u,record);
    w32(setup+44u,record+0x9d4u);
    w32(setup+40u,record+0x8cau);
    w32(setup+32u,done);
    w32(setup+28u,done);
    w8(setup+49u,phy);
    uint32_t sca=(uint32_t)accuracy;
    if(accuracy==0x7f)sca=r8(0x805a9cu);
    uint32_t channel=r8(record+63u);
    uint32_t index=r8(record+69u)-1u;
    uintptr_t connect=record+0x9dcu;
    uint32_t events=r16(record+32u);
    w8(connect+5u,channel);
    w8(connect+4u,channel);
    w32(connect-4u,0x8e89bed6u);
    w32(connect,0x555555u);
    uint32_t code=index<4u?(0x2010201u>>((index&0xffu)*8u&31u)):0u;
    w8(connect-6u,sca);
    w16(connect+68u,0x20u);
    w8(connect+7u,code);
    w8(connect+6u,code);
    if((events&5u)==1u&&(r8(record+59u)&2u)!=0u)w16(record+0xa22u,0x20u);
    uintptr_t adv=record+0xa3cu;
    uintptr_t source=record+1420u;
    w16(record+1430u,0u);
    w32(adv,record+945u);
    uint32_t length=opencfw_em9305_child_3239fc(record,record+945u,source,0u);
    uint32_t extra=*(volatile uint32_t *)(source+4u);
    uint32_t interval=r16(record+2250u);
    w16(adv-4u,length);
    w32(adv+8u,extra);
    w16(adv+4u,interval);
    uintptr_t buffer=opencfw_em9305_wsf_event_allocate(0x28u);
    if(buffer!=0u){
        w32(record+0xa6cu,(uint32_t)(uintptr_t)opencfw_em9305_child_32bc98);
        w32(record+0xa48u,buffer+4u);
    }else{
        w8(record+826u,31u);
        (void)opencfw_em9305_child_325a40(record,4u);
    }
    uintptr_t scan=record+0xa50u;
    w32(scan,record+1011u);
    uint32_t scan_length=opencfw_em9305_child_323b10(record,record+1011u,0u);
    w16(scan-4u,scan_length);
    return opencfw_em9305_child_328270(record,setup);
}
