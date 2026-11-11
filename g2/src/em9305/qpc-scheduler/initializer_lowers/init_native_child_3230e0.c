#include <stdint.h>

/* Native 0x3230e0..0x32317c: post LL event 0x29 (CIS established) for the
 * record's id (+2) with the given status. On success (status 0) also fill
 * the timing fields: the anchors (+0x28/+0x2c), PHY and count bytes, the
 * ISO interval (+16 us converted to 1.25 ms units by the stock reciprocal
 * multiply (x * 0x1a36e3) >> 31), the max PDU (+4) and one 16-bit handle
 * per stream (count +52, stream pointers from +0x38). */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct init_event_3230e0 {
    uint16_t handle;
    uint8_t event;
    uint8_t status;
    uint8_t status_copy;
    uint8_t id;
    uint8_t reserved0[2];
    uint32_t anchor0;
    uint32_t anchor1;
    uint8_t value292;
    uint8_t value19;
    uint8_t value18;
    uint8_t value1a;
    uint8_t value1b;
    uint8_t reserved1;
    uint16_t max_pdu;
    uint16_t interval;
    uint8_t count;
    uint8_t reserved2;
    uint16_t handles[4];
};

uint32_t opencfw_em9305_child_3230e0(uintptr_t record,uint32_t status)
{
    struct init_event_3230e0 message;
    (void)opencfw_em9305_memset((uint8_t *)&message+4u,0u,32u);
    uint32_t id=*(volatile uint8_t *)(record+2u);
    message.status_copy=(uint8_t)status;
    message.status=(uint8_t)status;
    message.event=0x29u;
    message.id=(uint8_t)id;
    message.handle=(uint16_t)id;
    if(status==0u) {
        message.value18=*(volatile uint8_t *)(record+0x18u);
        message.value1a=*(volatile uint8_t *)(record+0x1au);
        message.max_pdu=*(volatile uint16_t *)(record+4u);
        uint64_t scaled=(uint64_t)*(volatile uint32_t *)(record+16u)*0x1a36e3u;
        message.value1b=*(volatile uint8_t *)(record+0x1bu);
        message.value292=*(volatile uint8_t *)(record+292u);
        uint32_t count=*(volatile uint8_t *)(record+52u);
        message.anchor0=*(volatile uint32_t *)(record+0x28u);
        message.anchor1=*(volatile uint32_t *)(record+0x2cu);
        message.value19=*(volatile uint8_t *)(record+0x19u);
        message.count=(uint8_t)count;
        message.interval=(uint16_t)(scaled>>31);
        for(uint32_t i=0u;i<count;++i) {
            uintptr_t stream=*(volatile uint32_t *)(record+0x38u+4u*i);
            message.handles[i]=*(volatile uint16_t *)(stream+2u);
        }
    }
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&message);
}
