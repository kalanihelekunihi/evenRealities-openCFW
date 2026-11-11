#include <stdint.h>

/* Native 0x322c94..0x322d66: load BIG/CIS stream parameters into the
 * record: handles, counts and options bytes, the SDU interval divided by
 * the framing count (sleep_sync_divide), the larger of the two latency
 * words (+20/+28, flag at +31 when +20 is larger) times the byte +16 minus
 * 150, the optional encryption block (8 + 16 bytes and the seed derived
 * from it), the ISO interval in microseconds (+14 * 1250) and the PHY
 * timing from 317ea4. */
extern uint64_t opencfw_em9305_sleep_sync_divide(uint32_t low,uint32_t high,
    uint32_t denominator_low,uint32_t denominator_high);
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);
extern void opencfw_em9305_radio_encrypt_seed_317334(uintptr_t key,
    uintptr_t input,uintptr_t output);
extern uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t selector);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

uint32_t opencfw_em9305_dispatch_child_322c94(uintptr_t record,uintptr_t params)
{
    uint32_t handle=r16(params+34u);
    uint32_t count=r16(params+44u);
    uint32_t interval=r32(params+36u);
    uint32_t options=r8(params+32u);
    w16(record+6u,count);
    w32(record+344u,interval);
    uint32_t max_pdu=r16(params+46u);
    uint32_t phy=r8(params+17u);
    w16(record+4u,handle);
    w16(record+348u,max_pdu);
    w8(record+25u,phy);
    uint32_t packing=r8(params+24u);
    uint32_t framing=r8(params+68u);
    uint32_t divisor=r8(params+18u);
    w8(record+26u,packing);
    w8(record+30u,framing);
    uint32_t low=r32(params+60u),high=r32(params+64u);
    w8(record+27u,options);
    w8(record+24u,divisor);
    uint64_t quotient=opencfw_em9305_sleep_sync_divide(low,high,divisor,0u);
    uint32_t first=r32(params+20u);
    uint32_t second=r32(params+28u);
    w32(record+36u,(uint32_t)(quotient>>32));
    w32(record+32u,(uint32_t)quotient);
    uint32_t latency;
    if(second>=first){
        w8(record+31u,0u);
        latency=r32(params+28u);
    }else{
        w8(record+31u,1u);
        latency=r32(params+20u);
    }
    latency*=r8(params+16u);
    w32(record+40u,latency-150u);
    uint32_t encrypted=r8(params+69u);
    uint32_t number=r8(params+56u);
    w8(record+274u,0xffu);
    w8(record+292u,number);
    w8(record+484u,encrypted!=0u);
    if(encrypted!=0u){
        (void)opencfw_em9305_memcpy((void *)(record+485u),(const void *)(params+70u),8u);
        (void)opencfw_em9305_memcpy((void *)(record+493u),(const void *)(params+78u),16u);
        opencfw_em9305_radio_encrypt_seed_317334(record+493u,record+228u,record+92u);
    }
    uint32_t iso=r16(params+14u);
    uint32_t sdu=r32(params+28u);
    uint32_t transport=r32(params+20u);
    uint32_t offset=r32(params+40u);
    uint32_t selector=r8(params+8u);
    w32(record+12u,sdu);
    w32(record+48u,transport);
    w32(record+8u,offset);
    w32(record+16u,iso*1250u);
    uint32_t timing=opencfw_em9305_mode_callback_child_317ea4(selector);
    w16(record+244u,timing);
    return timing;
}
