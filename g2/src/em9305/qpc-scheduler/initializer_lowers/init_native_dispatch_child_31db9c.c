#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31db9c..0x31dc68: receive-test statistics for each stream of
 * the BIG/CIG (table +56, count +52). A stream with test mode on (+108)
 * and a stop request (+109) is reset; otherwise its next received PDU
 * (317624) is decoded and matched (32e2d8) against the expected payload
 * counter: in framed mode 1 (+30) the counter is +112 (taken from the
 * payload's first word when +110 requests a resync) and advances by one;
 * otherwise it is the event counter times the burst number (+24) plus the
 * low byte of +112. The PDU is released and the receive-buffer count at
 * ((uintptr_t)&em9305_ram_805a6c + 0x71u) is raised under a critical section. */
extern uintptr_t opencfw_em9305_dispatch_child_317624(uintptr_t record);
extern uint32_t opencfw_em9305_ll_received_decode_31bc7c(uintptr_t output,
                                                         uintptr_t input);
extern void opencfw_em9305_dispatch_child_32e2d8(uintptr_t key,uint32_t length,
    uintptr_t counters,uint32_t mode,uint32_t limit,uint32_t expected);
extern void opencfw_em9305_wsf_event_release(uintptr_t event);
extern uint32_t opencfw_em9305_wsf_critical_enter(void);
extern uint32_t opencfw_em9305_wsf_critical_exit(void);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}

void opencfw_em9305_dispatch_child_31db9c(uintptr_t group,uint32_t event_counter)
{
    for(uint32_t index=0u;index<r8(group+52u);++index){
        uintptr_t stream=r32(group+56u+index*4u);
        if(stream==0u||r8(stream+108u)==0u)continue;
        if(r8(stream+109u)!=0u){
            *(volatile uint32_t *)(stream+112u)=0u;
            *(volatile uint8_t *)(stream+110u)=0u;
            *(volatile uint16_t *)(stream+108u)=0u;
            continue;
        }
        uintptr_t pdu=opencfw_em9305_dispatch_child_317624(stream);
        if(pdu==0u)continue;
        _Alignas(4) uint8_t decoded[24];
        (void)opencfw_em9305_ll_received_decode_31bc7c((uintptr_t)decoded,pdu);
        uintptr_t payload=*(uint32_t *)(void *)(decoded+20);
        uint32_t expected;
        if(r8(group+30u)!=1u){
            expected=event_counter*r8(group+24u)+r8(stream+112u);
        }else{
            if(r8(stream+110u)==0u){
                expected=r32(stream+112u);
            }else{
                expected=r8(payload)+(r8(payload+1u)<<8)+(r8(payload+2u)<<16)
                         +(r8(payload+3u)<<24);
                *(volatile uint8_t *)(stream+110u)=0u;
            }
            *(volatile uint32_t *)(stream+112u)=expected+1u;
        }
        opencfw_em9305_dispatch_child_32e2d8(payload,decoded[14],stream+88u,
            r8(stream+116u),*(volatile uint16_t *)(group+6u),expected);
        opencfw_em9305_wsf_event_release(pdu);
        (void)opencfw_em9305_wsf_critical_enter();
        uint32_t buffers=r8(((uintptr_t)&em9305_ram_805a6c + 0x71u));
        *(volatile uint8_t *)((uintptr_t)&em9305_ram_805a6c + 0x71u)=(uint8_t)(buffers+1u);
        (void)opencfw_em9305_wsf_critical_exit();
    }
}
