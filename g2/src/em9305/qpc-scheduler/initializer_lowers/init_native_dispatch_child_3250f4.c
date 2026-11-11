#include <stdint.h>

/* Native 0x3250f4..0x3251dc: unframed ISO SDU reassembly on the context's
 * queue (+0x10). With no new PDU, a held fragment is flushed. A PDU whose
 * LLID (decoded byte 2) is 0 or 2 starts a new SDU: any held fragment is
 * dropped and the PDU is queued with its length (+0x18). LLID 1 or 3
 * continues: appended to the held fragment (data and length grow), or
 * queued as the head if none is held. LLID 2/3 complete the SDU; a
 * completed held fragment gets its ISO header rewritten (PB 2, total
 * length, status +0x1a). Returns 1 when an SDU completed. */
extern uintptr_t opencfw_em9305_wsf_event_peek(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_received_decode_31bc7c(uintptr_t,uintptr_t);
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t);
extern uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t,uint32_t,uintptr_t);
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);
extern uint32_t opencfw_em9305_dispatch_child_31b9ac(uintptr_t,uintptr_t);

struct init_iso_header_3250f4 {
    uint8_t handle;
    uint8_t reserved0;
    uint8_t llid;
    uint8_t reserved1;
    uint16_t length;
    uint8_t reserved2[8];
    uint16_t sdu_length;
    uint8_t status;
    uint8_t reserved3[3];
    uintptr_t data;
};

uint32_t opencfw_em9305_dispatch_child_3250f4(uintptr_t context,uintptr_t pdu)
{
    struct init_iso_header_3250f4 header,held_header;
    uint8_t handler;
    uintptr_t queue=context+0x10u;
    volatile uint16_t *total=(volatile uint16_t *)(context+0x18u);
    volatile uint8_t *status=(volatile uint8_t *)(context+0x1au);
    uintptr_t held=opencfw_em9305_wsf_event_peek(queue,(uintptr_t)&handler);
    uintptr_t complete=0u;
    uint32_t done=0u;
    if(pdu==0u) {
        if(held!=0u) {
            done=1u;
            *status=1u;
            complete=held;
        }
    } else {
        (void)opencfw_em9305_ll_received_decode_31bc7c((uintptr_t)&header,pdu);
        uint32_t llid=header.llid;
        if(llid==0u||llid==2u) {
            done=llid==2u;
            if(held!=0u)
                (void)opencfw_em9305_wsf_event_release(
                    opencfw_em9305_wsf_event_remove(queue,(uintptr_t)&handler));
            *total=header.sdu_length;
            *status=0u;
            (void)opencfw_em9305_ll_event_enqueue(queue,header.handle,pdu);
        } else if(llid==1u||llid==3u) {
            done=llid==3u;
            if(held==0u) {
                *total=header.length;
                (void)opencfw_em9305_ll_event_enqueue(queue,header.handle,pdu);
                *status=1u;
            } else {
                (void)opencfw_em9305_ll_received_decode_31bc7c((uintptr_t)&held_header,held);
                (void)opencfw_em9305_memcpy((void *)(held_header.data+*total),
                                            (const void *)header.data,header.length);
                (void)opencfw_em9305_wsf_event_release(pdu);
                *total=(uint16_t)(header.length+*total);
                complete=held;
            }
        } else {
            complete=held;
        }
    }
    if(done==0u||complete==0u) return done;
    (void)opencfw_em9305_ll_received_decode_31bc7c((uintptr_t)&header,complete);
    uint32_t length=*total;
    uint32_t flags=*status;
    header.llid=2u;
    header.sdu_length=(uint16_t)length;
    header.length=(uint16_t)length;
    header.status=(uint8_t)flags;
    (void)opencfw_em9305_dispatch_child_31b9ac(complete,(uintptr_t)&header);
    *status=0u;
    *total=0u;
    return done;
}
