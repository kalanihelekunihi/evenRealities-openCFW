#include <stdint.h>

/* Native 0x32841c..0x3284ea: initialise the record's 312-byte connection
 * setup block (+2468) for an initiator start: owner, request (+2516) and
 * parameter (+2250) pointers, both completion callbacks (3280e8), flags
 * and the PHY byte (+2784); then the connection request block (+2524):
 * access address 0x8e89bed6, CRC init 0x555555, the clock-accuracy byte
 * (+60, or 0x805a9c when it is 0x7f), the channel-map byte (+63, twice),
 * the PHY code for the PHY index (+69: 1,2,1,2 for 1..4, else 0, twice),
 * the 945 data pointers at +96/+132 and the 32c4fc callback at +2676; clear
 * +1430 and hand the block to 328270. */
extern void *opencfw_em9305_memset(void *dst,uint32_t value,uint32_t count);
extern void opencfw_em9305_child_3280e8(uintptr_t object);
extern uint32_t opencfw_em9305_child_32c4fc(uintptr_t context,uint32_t more);
extern uint32_t opencfw_em9305_child_328270(uintptr_t record,uintptr_t object);

static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

uint32_t opencfw_em9305_child_32841c(uintptr_t record)
{
    uintptr_t setup=record+0x9a4u;
    (void)opencfw_em9305_memset((void *)setup,0u,312u);
    int32_t accuracy=*(volatile int8_t *)(record+60u);
    uint32_t phy=*(volatile uint8_t *)(record+0xae0u);
    uintptr_t request=record+0x9d4u;
    uintptr_t params=record+0x8cau;
    uint32_t done=(uint32_t)(uintptr_t)opencfw_em9305_child_3280e8;
    w8(setup+26u,1u);
    w8(setup+24u,1u);
    w8(setup+48u,7u);
    w32(setup+36u,record);
    w32(setup+44u,request);
    w32(setup+40u,params);
    w32(setup+32u,done);
    w32(setup+28u,done);
    w8(setup+49u,phy);
    uint32_t sca=(uint32_t)accuracy;
    if(accuracy==0x7f)sca=*(volatile uint8_t *)0x805a9cu;
    uint32_t index=*(volatile uint8_t *)(record+69u)-1u;
    uintptr_t connect=record+0x9dcu;
    w32(connect+132u,record+945u);
    w32(connect+96u,record+945u);
    *(volatile uint16_t *)(record+1430u)=0u;
    uint32_t channel=*(volatile uint8_t *)(record+63u);
    uint32_t code=index<4u?(0x2010201u>>((index&0xffu)*8u&31u)):0u;
    w32(request+160u,(uint32_t)(uintptr_t)opencfw_em9305_child_32c4fc);
    w8(connect+7u,code);
    w8(connect+6u,code);
    w32(connect,0x555555u);
    w32(connect-4u,0x8e89bed6u);
    w8(connect-6u,sca);
    w8(connect+5u,channel);
    w8(connect+4u,channel);
    return opencfw_em9305_child_328270(record,setup);
}
