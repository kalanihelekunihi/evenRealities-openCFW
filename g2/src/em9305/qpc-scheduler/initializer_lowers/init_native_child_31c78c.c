#include <stdint.h>

/* Native 0x31c78c..0x31c7c4: clear the link's pending bit (bit 2 for
 * role 2, else bit 0). Active links clear it in 0x8019f8 and notify
 * 325edc with status 3; idle links clear it in 0x8019fa, reset +241 and
 * pass the new mask to 31fe38. */
extern uint32_t opencfw_em9305_child_325edc(uintptr_t link, uint32_t status);
extern uint32_t opencfw_em9305_child_31fe38(uintptr_t link, uint32_t mask);

uint32_t opencfw_em9305_child_31c78c(uintptr_t owner)
{
    uintptr_t link=*(volatile uint32_t *)(owner+36u);
    uint32_t bit=(*(volatile uint8_t *)(link+16u)==2u)?2u:0u;
    if(*(volatile uint8_t *)(link+2u)!=0u||*(volatile uint8_t *)(link+1u)!=0u){
        volatile uint8_t *pending=(volatile uint8_t *)(uintptr_t)0x8019f8u;
        *pending=(uint8_t)(*pending&~(1u<<bit));
        return opencfw_em9305_child_325edc(link,3u);
    }
    uint32_t mask=*(volatile uint8_t *)(uintptr_t)0x8019fau&~(1u<<bit);
    *(volatile uint8_t *)(link+241u)=0u;
    *(volatile uint8_t *)(uintptr_t)0x8019fau=(uint8_t)mask;
    return opencfw_em9305_child_31fe38(link,mask);
}
