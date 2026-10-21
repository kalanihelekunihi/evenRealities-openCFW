#include <stdint.h>

extern uintptr_t opencfw_em9305_radio_address_write_3045e8(
    uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

static void put_half(uint8_t *p,uint16_t value)
{
    p[0]=(uint8_t)value;
    p[1]=(uint8_t)(value>>8u);
}
static void put_word(uint8_t *p,uint32_t value)
{
    for (unsigned i=0;i<4u;i++) p[i]=(uint8_t)(value>>(i*8u));
}

/* Native 0x308664..0x308706 uses an exact 32-byte frame. The ARC entry
 * below allocates that frame before calling this source body, retaining
 * ambient bytes 5, 21 and 29..31 without a C automatic-array initialization. */
uint32_t opencfw_em9305_init_transition_event_308664_body(
    uint32_t kind,uintptr_t record,uint32_t include_first,uint8_t *event)
{
    event[4]=(uint8_t)kind;
    put_word(event,0x13u<<17u);
    uint32_t period=*(volatile uint32_t *)(record+252u);
    uint16_t shared_second=*(volatile uint16_t *)(uintptr_t)0x8051c4u;
    uint8_t recorded_c=*(volatile uint8_t *)(record+256u);
    uint8_t recorded_b=*(volatile uint8_t *)(record+776u);
    uint16_t shared_first=*(volatile uint16_t *)(uintptr_t)0x8051c2u;
    uint16_t shift=*(volatile uint16_t *)(record+716u);
    event[24]=recorded_c;
    event[20]=recorded_b;
    put_half(event+12u,shift);
    put_half(event+8u,shared_second);
    put_half(event+6u,shared_first);
    put_half(event+10u,(uint8_t)((int32_t)(record-0x803d78u)/784));
    put_half(event+14u,0u);
    put_half(event+16u,0u);
    put_half(event+18u,0u);
    uint64_t product=(uint64_t)period*0x001a36e3u;
    uint32_t low=(uint32_t)product;
    uint32_t high=(uint32_t)(product>>32u);
    uint32_t scaled=(high<<1u)|(low>>31u);
    put_half(event+22u,(uint16_t)scaled);
    uint8_t first=0u;
    if (include_first!=0u) first=*(volatile uint8_t *)(record+512u);
    uint8_t fourth=*(volatile uint8_t *)(record+515u);
    uint8_t second=*(volatile uint8_t *)(record+513u);
    uint8_t third=*(volatile uint8_t *)(record+514u);
    uint32_t address_high=*(volatile uint32_t *)(record+724u);
    uint32_t address_low=*(volatile uint32_t *)(record+720u);
    event[28]=fourth;
    event[25]=first;
    event[26]=second;
    event[27]=third; /* Native BL serializer delay slot executes first. */
    (void)opencfw_em9305_radio_address_write_3045e8(
        (uintptr_t)(event+14u),address_low,address_high);
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}

#ifdef __arc__
__asm__(
".text\n.balign 4\n.global opencfw_em9305_init_transition_event_308664\n"
".type opencfw_em9305_init_transition_event_308664,@function\n"
"opencfw_em9305_init_transition_event_308664:\n"
"enter_s [r13-r15,fp,blink]\nsub_s sp,sp,0x20\n"
"mov r3,sp\nbl opencfw_em9305_init_transition_event_308664_body\n"
"leave_s [r13-r15,fp,blink,pcl]\n"
".size opencfw_em9305_init_transition_event_308664,. - opencfw_em9305_init_transition_event_308664\n");
#else
uint32_t opencfw_em9305_init_transition_event_308664(
    uint32_t kind,uintptr_t record,uint32_t include_first)
{
    uint8_t event[32] __attribute__((aligned(4)));
    return opencfw_em9305_init_transition_event_308664_body(
        kind,record,include_first,event);
}
#endif
