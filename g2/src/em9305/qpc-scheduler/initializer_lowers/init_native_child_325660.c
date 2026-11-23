#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x325660..0x325686: when bit 2 of the mode byte at ((uintptr_t)&em9305_ram_805a6c + 0x1fu) is
 * set, count down the record byte at +100; returns 1 when the count is (or
 * becomes) zero or the mode bit is clear, otherwise 0. */
uint32_t opencfw_em9305_child_325660(uintptr_t record)
{
    if((em9305_ram_805a6c.u8_805a8b&4u)==0u)return 1u;
    uint32_t count=*(volatile uint8_t *)(record+100u);
    if(count==0u)return 1u;
    count=(uint8_t)(count-1u);
    *(volatile uint8_t *)(record+100u)=(uint8_t)count;
    return count==0u;
}
