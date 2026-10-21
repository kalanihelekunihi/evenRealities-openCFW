#include <stdint.h>

extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_ll_event_enqueue(
    uintptr_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_wsf_event_post(uint32_t,uint32_t);

/* Native 0x32805c..0x3280c6. ADD2 0x21 scales by four to record+132.
 * Native captures the four words before writing either event byte. */
uint32_t opencfw_em9305_init_transition_callback_32805c(uintptr_t owner)
{
    uintptr_t record=*(volatile uint32_t *)(owner+44u);
    uintptr_t fields=record+132u;
    uint32_t state=*(volatile uint8_t *)(fields+16u);
    if(state!=3u)return state;
    state=*(volatile uint8_t *)(fields+20u);
    if(state==0u)return state;
    state=*(volatile uint8_t *)(record+149u);
    if(state!=12u)return state;
    state=*(volatile uint32_t *)(record+108u);
    if(state==0u)return state;
    state=*(volatile uint8_t *)(uintptr_t)0x805becu;
    if(state==0u)return state;
    uintptr_t event=opencfw_em9305_wsf_event_allocate(24u);
    if(event==0u)return 0u;
    uint8_t second=*(volatile uint8_t *)(record+151u);
    uint8_t first=*(volatile uint8_t *)(record+150u);
    uint32_t fourth=*(volatile uint32_t *)(fields+12u);
    uint32_t third=*(volatile uint32_t *)(fields+8u);
    uint32_t next=*(volatile uint32_t *)(fields+4u);
    uint32_t head=*(volatile uint32_t *)fields;
    *(volatile uint8_t *)(event+12u)=second;
    *(volatile uint8_t *)event=first;
    *(volatile uint32_t *)(event+20u)=fourth;
    *(volatile uint32_t *)(event+16u)=third;
    *(volatile uint32_t *)(event+8u)=next;
    *(volatile uint32_t *)(event+4u)=head; /* BL delay slot. */
    (void)opencfw_em9305_ll_event_enqueue(0x8053f8u,0u,event);
    uint8_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
    return opencfw_em9305_wsf_event_post(handler,1024u);
}
