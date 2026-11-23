#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x303a80..0x303ad8: for each of the resolving-list entries
 * (count at ((uintptr_t)&em9305_ram_801608 + 0x8u), 72-byte entries at *((uintptr_t)&em9305_ram_805be0 + 0x20u)), generate a fresh
 * private address for the local IRK (+16 -> +48) when +65 is clear and
 * for the peer IRK (+0 -> +40) when +64 is clear and +66 set, then mark
 * the entry refreshed (+68). */
extern uint64_t opencfw_em9305_radio_private_address_31467c(uintptr_t irk);

void opencfw_em9305_child_303a80(void)
{
    for(uint32_t index=0u;index<em9305_ram_801608.u8_801610;++index){
        uintptr_t base=em9305_ram_805be0.u32_805c00;
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
