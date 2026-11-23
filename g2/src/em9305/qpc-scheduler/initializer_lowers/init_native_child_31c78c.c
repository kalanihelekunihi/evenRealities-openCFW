#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31c78c..0x31c7c4: clear the link's pending bit (bit 2 for
 * role 2, else bit 0). Active links clear it in ((uintptr_t)&em9305_ram_8019e8 + 0x10u) and notify
 * 325edc with status 3; idle links clear it in ((uintptr_t)&em9305_ram_8019e8 + 0x12u), reset +241 and
 * pass the new mask to 31fe38. */
extern uint32_t opencfw_em9305_child_325edc(uintptr_t link, uint32_t status);
extern uint32_t opencfw_em9305_child_31fe38(uintptr_t link, uint32_t mask);

uint32_t opencfw_em9305_child_31c78c(uintptr_t owner)
{
    uintptr_t link=*(volatile uint32_t *)(owner+36u);
    uint32_t bit=(*(volatile uint8_t *)(link+16u)==2u)?2u:0u;
    if(*(volatile uint8_t *)(link+2u)!=0u||*(volatile uint8_t *)(link+1u)!=0u){
        volatile uint8_t *pending=&em9305_ram_8019e8.u8_8019f8;
        *pending=(uint8_t)(*pending&~(1u<<bit));
        return opencfw_em9305_child_325edc(link,3u);
    }
    uint32_t mask=em9305_ram_8019e8.u8_8019fa&~(1u<<bit);
    *(volatile uint8_t *)(link+241u)=0u;
    em9305_ram_8019e8.u8_8019fa=(uint8_t)mask;
    return opencfw_em9305_child_31fe38(link,mask);
}
