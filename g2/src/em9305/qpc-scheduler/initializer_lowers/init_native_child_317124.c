#include <stdint.h>

/* Native 0x317124..0x317212: copy queued received PDUs into an output
 * buffer (data from out+8) within a byte budget. Each step peeks the
 * queue head, decodes its header and emits a descriptor (31ba24) plus
 * payload: a PDU that fits (5-byte descriptor, or 2 for a continuation
 * at offset +10) is removed, counted down (+8) and flagged (+12); one
 * that does not fit is split, advancing the offset at +10. Returns the
 * number of bytes produced (8 bits). */
extern uintptr_t opencfw_em9305_wsf_event_peek(uintptr_t queue, uintptr_t handler_out);
extern uint32_t opencfw_em9305_ll_received_decode_31bc7c(uintptr_t header, uintptr_t event);
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue, uintptr_t handler_out);
extern uint32_t opencfw_em9305_child_31ba24(uintptr_t out, uintptr_t descriptor);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t length);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t event);

struct opencfw_em9305_rx_descriptor {
    uint8_t continuation;
    uint8_t complete;
    uint8_t length;
    uint8_t reserved;
    uint32_t value;
};

uint32_t opencfw_em9305_child_317124(uintptr_t queue, uintptr_t out, uint32_t budget)
{
    struct opencfw_em9305_rx_descriptor descriptor={0u,0u,0u,0u,0u};
    uint8_t header[24] __attribute__((aligned(4)));
    uint8_t handler;
    uintptr_t destination=out+8u;
    uint32_t total=0u;
    for(;;){
        uint32_t available=(uint16_t)budget;
        if(available==0u)break;
        uintptr_t event=opencfw_em9305_wsf_event_peek(queue,(uintptr_t)&handler);
        if(event==0u)break;
        (void)opencfw_em9305_ll_received_decode_31bc7c((uintptr_t)header,event);
        volatile uint16_t *offset=(volatile uint16_t *)(queue+10u);
        uint32_t consumed=*offset;
        uint32_t remaining=*(volatile uint16_t *)&header[14];
        uintptr_t source=event+(header[3]!=0u?12u:8u);
        uint32_t overhead;
        if(consumed!=0u){
            remaining-=consumed;
            source+=consumed;
            overhead=2u;
            descriptor.continuation=1u;
        }else{
            overhead=5u;
            descriptor.continuation=0u;
        }
        uintptr_t removed=0u;
        uint32_t next;
        if(available>=(uint16_t)remaining+overhead){
            descriptor.complete=1u;
            descriptor.length=(uint8_t)remaining;
            *offset=0u;
            removed=opencfw_em9305_wsf_event_remove(queue,(uintptr_t)&handler);
            uint32_t pending=*(volatile uint8_t *)(queue+8u);
            next=budget-((uint8_t)remaining+overhead);
            *(volatile uint8_t *)(queue+12u)=1u;
            *(volatile uint8_t *)(queue+8u)=(uint8_t)(pending-1u);
        }else{
            if(overhead>=available)break;
            uint32_t chunk=budget-overhead;
            descriptor.complete=0u;
            descriptor.length=(uint8_t)chunk;
            *offset=(uint16_t)(consumed+(uint8_t)chunk);
            next=0u;
        }
        uint32_t used=opencfw_em9305_child_31ba24(destination,(uintptr_t)&descriptor);
        uint32_t length=*(volatile uint8_t *)&descriptor.length;
        destination+=used;
        (void)opencfw_em9305_memcpy((void *)destination,(const void *)source,length);
        if(removed!=0u)(void)opencfw_em9305_wsf_event_release(removed);
        total+=overhead+length;
        destination+=length;
        budget=next;
    }
    return (uint8_t)total;
}
