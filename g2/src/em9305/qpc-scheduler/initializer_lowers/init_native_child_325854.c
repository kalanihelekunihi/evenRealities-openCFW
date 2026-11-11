#include <stdint.h>

/* Native 0x325854..0x325896: hop to the next data channel. Repeatedly draw
 * a random step (also stored at record+832), advance the channel at
 * record+0xae0 by it modulo 37 and stop once the channel is set in the
 * 64-bit channel map at 0x805aa0 (bit 0 of map >> channel). The modulo is
 * the stock reciprocal form: q = (sum * 0xdd68) >> 21, sum - 37 * q with
 * a 16-bit signed multiply. */
extern uint32_t opencfw_em9305_associated_random_31896c(void);
extern uint64_t opencfw_em9305_child_3027f4(uint64_t value,uint32_t count);

uint32_t opencfw_em9305_child_325854(uintptr_t record)
{
    volatile uint8_t *channel=(volatile uint8_t *)(record+0xae0u);
    uint32_t found;
    do {
        uint32_t step=opencfw_em9305_associated_random_31896c();
        uint32_t current=*channel;
        *(volatile uint8_t *)(record+832u)=(uint8_t)step;
        uint32_t sum=current+step;
        uint32_t quotient=(uint32_t)(sum*0xdd68u)>>21;
        uint32_t next=sum+(uint32_t)((int32_t)(int16_t)quotient*-37);
        *channel=(uint8_t)next;
        uint64_t map=((uint64_t)*(volatile uint32_t *)(uintptr_t)0x805aa4u<<32)|
                     *(volatile uint32_t *)(uintptr_t)0x805aa0u;
        found=(uint32_t)opencfw_em9305_child_3027f4(map,(uint8_t)next);
    } while((found&1u)==0u);
    return found;
}
