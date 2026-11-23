#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3280e8..0x328270: periodic advertising event end for the set at
 * object+0x24. Count the event (+825); a stopping set (+0x8d6, +0x8d4) or
 * one whose event limit (+824) is reached (status 0x43 at +826) is ended:
 * clear +0xae1, mark +0x8d6, notify the scheduler (+0x8d8) and run 325a40
 * with 4. Otherwise refresh the PDU's TX power (+0xe from +0xf or the
 * default ((uintptr_t)&em9305_ram_805be0 + 0xdu)), commit pending advertising data (+1440: copy into the
 * buffer at +1424, update lengths +1420/+0x8ca/+1432 and DID +64, rebuild
 * via 32387c; without a periodic train +828 just clear +0xae1) and pending
 * scan-response data (+1716), apply a pending DID update (+0xae2), and
 * when the address identity is resolved rebuild the PDU (3239fc) into the
 * object's PDU fields before running 3284ec. */
extern uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t);
extern uint32_t opencfw_em9305_child_325a40(uintptr_t,uint32_t);
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);
extern uint32_t opencfw_em9305_child_32387c(uintptr_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_radio_identity_consume_3039d0(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_3239fc(uintptr_t,uintptr_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_child_3284ec(uintptr_t,uintptr_t);

static uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
static void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

void opencfw_em9305_child_3280e8(uintptr_t object)
{
    uintptr_t set=r32(object+0x24u);
    uintptr_t pdu=r32(object+44u);
    uint32_t stopping=r8(set+0x8d6u);
    uint32_t count=r8(set+825u)+1u;
    w8(set+825u,count);
    uint32_t end=stopping!=0u||r8(set+0x8d4u)!=0u;
    if(!end) {
        uint32_t limit=r8(set+824u);
        if(limit!=0u&&(uint8_t)count>=limit) {
            w8(set+826u,0x43u);
            end=1u;
        }
    }
    if(end) {
        w8(set+0xae1u,0u);
        w8(set+0x8d6u,1u);
        (void)opencfw_em9305_ll_schedule_notify_313354(set+0x8d8u);
        (void)opencfw_em9305_child_325a40(set,4u);
        return;
    }
    uint32_t power=r8(pdu+0xfu);
    if(power==0u) power=r8(((uintptr_t)&em9305_ram_805be0 + 0xdu));
    w8(pdu+0xeu,power);
    if(r8(set+1440u)!=0u) {
        uintptr_t buffer=r32(set+1424u);
        uint32_t length=r8(set+1441u);
        w8(set+1440u,0u);
        (void)opencfw_em9305_memcpy((void *)buffer,(const void *)(set+1444u),length);
        length=r8(set+1441u);
        uint32_t operation=r8(set+1695u);
        uint32_t did=r16(set+1442u);
        w16(set+1420u,length);
        w16(set+0x8cau,length);
        w8(set+1432u,operation);
        w16(set+64u,did);
        uint32_t built=opencfw_em9305_child_32387c(set,set+840u,0u);
        uint32_t train=r32(set+828u);
        w8(set+0x8cau+186u,built);
        if(train==0u) {
            w8(set+0xae1u,0u);
            return;
        }
    }
    if(r8(set+1716u)!=0u) {
        uintptr_t buffer=r32(set+1700u);
        uint32_t length=r8(set+1717u);
        w8(set+1716u,0u);
        (void)opencfw_em9305_memcpy((void *)buffer,(const void *)(set+1720u),length);
        length=r8(set+1717u);
        uint32_t did=r16(set+1718u);
        uint32_t operation=r8(set+1971u);
        w16(set+0x8c8u,length);
        w16(set+1696u,length);
        w16(set+64u,did);
        w8(set+1708u,operation);
    }
    if(r8(set+0xae2u)!=0u) {
        uint32_t did=r16(set+1442u);
        w8(set+0xae2u,0u);
        w16(set+64u,did);
    }
    if(opencfw_em9305_radio_identity_consume_3039d0(r8(set+58u),r32(set+0x30u),
                                                    r32(set+0x34u))!=0u) {
        w16(set+1430u,0u);
        uint32_t built=opencfw_em9305_child_3239fc(set,set+945u,set+1420u,0u);
        uint32_t buffer=r32(set+1424u);
        uint32_t length=r16(set+0x8cau);
        w16(pdu+100u,built);
        w32(pdu+0x70u,buffer);
        w16(pdu+108u,length);
    }
    (void)opencfw_em9305_child_3284ec(set,object);
}
