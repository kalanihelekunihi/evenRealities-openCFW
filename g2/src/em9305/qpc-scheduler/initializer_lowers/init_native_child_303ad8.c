#include <stdint.h>

/* Native 0x303ad8..0x303b40: like 303a80, but only for resolving-list
 * entries whose identity address (+32 low word, +36 high word) equals
 * {low, type<<16 | high}: regenerate the local (+16 -> +48, unless +65)
 * and peer (+0 -> +40, when +64 clear and +66 set) private addresses and
 * mark the entry refreshed (+68). */
extern uint64_t opencfw_em9305_radio_private_address_31467c(uintptr_t irk);

void opencfw_em9305_child_303ad8(uint32_t type, uint32_t low, uint32_t high)
{
    uint32_t key_high=(type<<16)|high;
    for(uint32_t index=0u;index<*(volatile uint8_t *)(uintptr_t)0x801610u;++index){
        uintptr_t entry=*(volatile uint32_t *)(uintptr_t)0x805c00u+index*72u;
        if(*(volatile uint32_t *)(entry+32u)!=low||*(volatile uint32_t *)(entry+36u)!=key_high)
            continue;
        if(*(volatile uint8_t *)(entry+65u)==0u){
            uint64_t address=opencfw_em9305_radio_private_address_31467c(entry+16u);
            *(volatile uint32_t *)(entry+52u)=(uint32_t)(address>>32);
            *(volatile uint32_t *)(entry+48u)=(uint32_t)address;
        }
        if(*(volatile uint8_t *)(entry+64u)==0u&&*(volatile uint8_t *)(entry+66u)!=0u){
            uint64_t address=opencfw_em9305_radio_private_address_31467c(entry);
            *(volatile uint32_t *)(entry+44u)=(uint32_t)(address>>32);
            *(volatile uint32_t *)(entry+40u)=(uint32_t)address;
        }
        *(volatile uint8_t *)(entry+68u)=1u;
    }
}
