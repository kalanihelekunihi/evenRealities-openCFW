#include <stdint.h>

/* Complete native 0x3183ec..0x31843c. Native early returns retain
 * path-specific R0: incoming context or 0x805a70, not a boolean. */
extern uint32_t opencfw_em9305_radio_peer_pair_303a40(uint32_t,uint32_t,
    uint32_t,uintptr_t);
uint32_t opencfw_em9305_init_callback_3183ec(uintptr_t context,
                                               uintptr_t record)
{
    uint32_t mode=*(volatile uint8_t *)(uintptr_t)0x805afdu;
    uint32_t result=(uint32_t)context;
    if (mode==1u) {
        uintptr_t flags_root=0x805a70u;
        uint8_t active=*(volatile uint8_t *)(flags_root+17u);
        result=(uint32_t)flags_root;
        if (active!=0u) {
            *(volatile uint8_t *)(flags_root+16u)=0u;
            *(volatile uint8_t *)(context+2u)=1u;
        } else *(volatile uint8_t *)(context+2u)=0u;
    } else *(volatile uint8_t *)(context+2u)=0u;
    if ((mode&2u)==0u) return result;
    uint32_t high=*(volatile uint32_t *)(record+156u);
    uint32_t low=*(volatile uint32_t *)(record+152u);
    uint32_t kind=*(volatile uint8_t *)(record+163u);
    volatile uint32_t pair[2];
    result=opencfw_em9305_radio_peer_pair_303a40(kind,low,high,(uintptr_t)pair);
    if (result==0u) return 0u;
    uint32_t upper=pair[1];
    uint32_t lower=pair[0];
    *(volatile uint8_t *)(context+2u)=1u;
    *(volatile uint32_t *)(uintptr_t)0x805b08u=upper;
    *(volatile uint32_t *)(uintptr_t)0x805b04u=lower;
    return lower;
}
