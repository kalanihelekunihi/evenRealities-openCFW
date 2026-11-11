#include <stdint.h>

/* Native 0x321c30..0x321e12: periodic advertising report assembly for the
 * sync context at object+0x24. The channel-map check (PAwR +777: bit of
 * the subevent counter in the map at +780) gates reporting. Without data,
 * an established train (+36 = +1 = 1) or a failed PAwR subevent reports
 * an empty/truncated record (status 2 or 0xff, 0x7f7f power) via 324734.
 * With an ADV_EXT header (type 7), PAwR response slots dedupe on the
 * stored DID (+280 table, receiver +758/+777). Then, when reporting is
 * enabled (+5), start a fresh report (+0x10..: index, power, RSSI, CTE,
 * event counter, subevent) or continue one (+26 bytes so far), append the
 * received data (0x803b6c/+0x803b70) while it fits the configured length,
 * mark truncation (status 2) otherwise, and flush via 324734 unless more
 * data follows (0x803b72 bit 4). Returns 1 when data was appended. */
extern uint64_t opencfw_em9305_child_3027f4(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_32db0c(uintptr_t,uintptr_t);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);
extern uint32_t opencfw_em9305_child_324734(uintptr_t);

static uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
static void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

static uint32_t slot_321c30(uintptr_t base)
{
    return (uint8_t)((int32_t)((uint32_t)base-0x803d78u)/784);
}

uint32_t opencfw_em9305_callback_321c30(uintptr_t object,uintptr_t data)
{
    uintptr_t sync=r32(object+0x24u);
    uintptr_t pdu=r32(object+44u);
    const uintptr_t report=(uintptr_t)0x803b68u;
    uint32_t pawr=r8(sync+777u);
    uint32_t in_map=1u;
    if(pawr!=0u) {
        uintptr_t block=r32(sync+780u);
        in_map=(uint32_t)opencfw_em9305_child_3027f4(r32(block+8u),r32(block+0xcu),
                                                     r8(block+0x12u))&1u;
    }
    if(data==0u) {
        if(!(r8(sync+36u)==1u&&r8(sync+1u)==1u&&in_map!=0u)) {
            if(pawr==0u||in_map!=1u) return 0u;
        }
        (void)opencfw_em9305_memset((void *)(sync+0x10u),0u,0x14u);
        uint32_t index=slot_321c30(sync);
        uintptr_t block=r32(sync+780u);
        w16(sync+0x16u,0x7f7fu);
        uint32_t counter=r16(sync+248u);
        uint32_t subevent=r8(block+0x12u);
        w8(sync+0x19u,(pawr==0u)?2u:0xffu);
        w16(sync+0x14u,index);
        w8(sync+24u,0xffu);
        w16(sync+0x20u,counter);
        w8(sync+34u,subevent);
        (void)opencfw_em9305_child_324734(sync);
        return 0u;
    }
    uint8_t header[8];
    (void)opencfw_em9305_child_32db0c((uintptr_t)header,data);
    if(header[0]!=7u) return 0u;
    uintptr_t receiver=r32(object+36u);
    uintptr_t response=receiver+758u;
    if(r8(receiver+1u)==1u&&r8(receiver+7u)!=0u&&(r8(0x803b72u)&8u)) {
        uint32_t enabled=r8(response+0x13u);
        uint32_t did=r16(response);
        uint32_t slot=0u;
        if(enabled!=0u) slot=r8(r32(receiver+780u)+0x12u)&0x7fu;
        if(did==r16(receiver+280u+2u*slot)) return 0u;
        if(in_map==1u) {
            slot=0u;
            if(enabled!=0u) slot=r8(r32(receiver+780u)+0x12u)&0x7fu;
            w16(receiver+280u+2u*slot,did);
        }
    }
    if(r8(sync+5u)==0u||in_map!=1u) return 0u;
    uint32_t state=r8(sync+36u);
    uint32_t offset;
    if(state==0u) {
        uintptr_t current=r32(object+44u);
        uint32_t flags=r8(report+10u);
        (void)opencfw_em9305_memset((void *)(sync+0x10u),0u,0x14u);
        w16(sync+0x14u,slot_321c30(receiver));
        if(flags&0x40u) w8(sync+0x16u,r8(response+3u));
        uint32_t cte=0xffu,subevent=0xffu;
        w8(sync+0x17u,r8(current+138u));
        if(flags&4u) cte=r8(response-1u);
        uint32_t enabled=r8(response+0x13u);
        uint32_t anchor=r32(receiver+40u);
        uint32_t counter=r16(receiver+248u);
        w8(sync+0x18u,cte);
        w32(sync+0x1cu,anchor);
        w16(sync+0x20u,counter);
        if(enabled!=0u) subevent=r8(r32(receiver+780u)+0x12u);
        w8(sync+34u,subevent);
        if(r8(sync+1u)!=1u) {
            (void)opencfw_em9305_child_324734(sync);
            return 0u;
        }
        w8(sync+36u,1u);
        offset=0u;
    } else if(state==2u) {
        return 0u;
    } else {
        offset=r16(sync+26u);
    }
    uint32_t length=r8(report+8u);
    if((uint16_t)(r16(r32(0x805cacu)+0x20u)-offset)<length) {
        w8(sync+25u,2u);
        (void)opencfw_em9305_child_324734(sync);
        return 0u;
    }
    uint32_t rssi=r8(pdu+138u);
    (void)opencfw_em9305_memcpy((void *)(r32(sync+0x28u)+offset),
                                (const void *)r32(report+4u),length);
    uint32_t more=r8(report+10u);
    length+=r16(sync+0x1au);
    w8(sync+0x17u,rssi);
    w16(sync+0x1au,length);
    if((more&0x10u)==0u) (void)opencfw_em9305_child_324734(sync);
    return 1u;
}
