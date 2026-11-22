#include <stdint.h>

/* Native 0x325984..0x3259fa: channel selection algorithm #1. Advance the
 * unmapped channel (+270) by (events + 1) * hop (+271) modulo 37 (stock
 * reciprocal form for values of 37 and up); if it is not set in the
 * channel map (+276/+280), remap it through the used-channel table (+284)
 * by its remainder modulo the used-channel count (+272). */
extern uint64_t opencfw_em9305_child_3027f4(uint32_t,uint32_t,uint32_t);

uint32_t opencfw_em9305_callback_325984(uintptr_t record,uint32_t events)
{
    uint32_t hop=*(volatile uint8_t *)(record+271u);
    uint32_t channel=*(volatile uint8_t *)(record+270u)+(events+1u)*hop;
    if((uint16_t)channel>=37u) {
        uint32_t quotient=((uint16_t)channel*0xdd68u)>>21;
        channel+=(uint32_t)((int32_t)(int16_t)quotient*-37);
    }
    *(volatile uint8_t *)(record+270u)=(uint8_t)channel;
    uint32_t unmapped=(uint16_t)channel;
    uint32_t used=(uint32_t)opencfw_em9305_child_3027f4(
        *(volatile uint32_t *)(record+276u),*(volatile uint32_t *)(record+280u),unmapped);
    if(used&1u) return (uint8_t)channel;
    uint32_t count=*(volatile uint8_t *)(record+272u);
    if(unmapped>=count) {
        if(count>0x12u)
            channel-=count;
        else
            while((uint8_t)channel>=count) channel-=count;
    }
    return *(volatile uint8_t *)(record+(uint8_t)channel+284u);
}
