#include <stdint.h>

/* Native 0x325660..0x325686: when bit 2 of the mode byte at 0x805a8b is
 * set, count down the record byte at +100; returns 1 when the count is (or
 * becomes) zero or the mode bit is clear, otherwise 0. */
uint32_t opencfw_em9305_child_325660(uintptr_t record)
{
    if((*(volatile uint8_t *)(uintptr_t)0x805a8bu&4u)==0u)return 1u;
    uint32_t count=*(volatile uint8_t *)(record+100u);
    if(count==0u)return 1u;
    count=(uint8_t)(count-1u);
    *(volatile uint8_t *)(record+100u)=(uint8_t)count;
    return count==0u;
}
