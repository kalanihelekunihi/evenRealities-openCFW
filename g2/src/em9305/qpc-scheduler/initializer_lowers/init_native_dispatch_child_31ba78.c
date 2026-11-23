#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31ba78..0x31bad0: decode a received PDU into a scratch record,
 * then, for a link in state 0 or 1, queue the PDU on the link's queue
 * (+4) for the handler (state 0 also counts it in byte +12) and drop the
 * receive-pending count at ((uintptr_t)&em9305_ram_805a6c + 0x71u) under a critical section. Returns 1
 * when queued, 0 for any other state. */
extern uint32_t opencfw_em9305_ll_received_decode_31bc7c(uintptr_t output,
                                                         uintptr_t input);
extern uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t queue,uint32_t handler,
                                                uintptr_t event);
extern uint32_t opencfw_em9305_wsf_critical_enter(void);
extern uint32_t opencfw_em9305_wsf_critical_exit(void);

uint32_t opencfw_em9305_dispatch_child_31ba78(uintptr_t link,uint32_t handler,
                                              uint32_t unused,uintptr_t pdu)
{
    _Alignas(4) uint8_t decoded[24];
    (void)unused;
    (void)opencfw_em9305_ll_received_decode_31bc7c((uintptr_t)decoded,pdu);
    uint32_t state=*(volatile uint8_t *)link;
    uintptr_t queue=link+4u;
    if(state==1u){
        (void)opencfw_em9305_ll_event_enqueue(queue,(uint8_t)handler,pdu);
    }else{
        if(state!=0u)return 0u;
        (void)opencfw_em9305_ll_event_enqueue(queue,(uint8_t)handler,pdu);
        uint32_t count=*(volatile uint8_t *)(queue+8u);
        *(volatile uint8_t *)(queue+8u)=(uint8_t)(count+1u);
    }
    (void)opencfw_em9305_wsf_critical_enter();
    uint32_t pending=*(volatile uint8_t *)((uintptr_t)&em9305_ram_805a6c + 0x71u);
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_805a6c + 0x71u)=(uint8_t)(pending-1u);
    (void)opencfw_em9305_wsf_critical_exit();
    return 1u;
}
