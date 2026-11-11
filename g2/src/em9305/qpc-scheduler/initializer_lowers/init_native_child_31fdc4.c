#include <stdint.h>

/* Native 0x31fdc4..0x31fe36: count a link event and clear the link's
 * pending bit (bit 2 for role 2, else bit 0). Active links count +242 and
 * once due (two events when +241 is set, any wrap-free count otherwise)
 * clear the bit in 0x8019f8 and notify 325edc with status 3. Idle links
 * clear the bit in 0x8019fa, reset +424/+440 and, when +241 is clear,
 * pass the new mask to 31fe38. Returns the link when nothing is called. */
extern uint32_t opencfw_em9305_child_325edc(uintptr_t link, uint32_t status);
extern uint32_t opencfw_em9305_child_31fe38(uintptr_t link, uint32_t mask);

uint32_t opencfw_em9305_child_31fdc4(uintptr_t owner)
{
    uintptr_t link=*(volatile uint32_t *)(owner+36u);
    uint32_t bit=(*(volatile uint8_t *)(link+16u)==2u)?2u:0u;
    if(*(volatile uint8_t *)(link+2u)!=0u||*(volatile uint8_t *)(link+1u)!=0u){
        uint32_t count=(uint8_t)(*(volatile uint8_t *)(link+242u)+1u);
        uint32_t armed=*(volatile uint8_t *)(link+241u);
        *(volatile uint8_t *)(link+242u)=(uint8_t)count;
        if(armed!=0u?count<2u:count==0u)return (uint32_t)link;
        volatile uint8_t *pending=(volatile uint8_t *)(uintptr_t)0x8019f8u;
        *pending=(uint8_t)(*pending&~(1u<<bit));
        return opencfw_em9305_child_325edc(link,3u);
    }
    uint32_t armed=*(volatile uint8_t *)(link+241u);
    uint32_t mask=*(volatile uint8_t *)(uintptr_t)0x8019fau&~(1u<<bit);
    *(volatile uint32_t *)(link+424u)=0u;
    *(volatile uint8_t *)(link+440u)=0u;
    *(volatile uint8_t *)(uintptr_t)0x8019fau=(uint8_t)mask;
    if(armed!=0u)return (uint32_t)link;
    return opencfw_em9305_child_31fe38(link,mask);
}
