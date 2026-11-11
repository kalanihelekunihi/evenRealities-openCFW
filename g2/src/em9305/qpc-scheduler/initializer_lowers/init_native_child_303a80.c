#include <stdint.h>

/* Native 0x303a80..0x303ad8: for each of the resolving-list entries
 * (count at 0x801610, 72-byte entries at *0x805c00), generate a fresh
 * private address for the local IRK (+16 -> +48) when +65 is clear and
 * for the peer IRK (+0 -> +40) when +64 is clear and +66 set, then mark
 * the entry refreshed (+68). */
extern uint64_t opencfw_em9305_radio_private_address_31467c(uintptr_t irk);

void opencfw_em9305_child_303a80(void)
{
    for(uint32_t index=0u;index<*(volatile uint8_t *)(uintptr_t)0x801610u;++index){
        uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c00u;
        uintptr_t entry=base+index*72u;
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
        *(volatile uint8_t *)(base+index*72u+68u)=1u;
    }
}
