#include <assert.h>
#include <stdint.h>
#include <string.h>

uint32_t opencfw_em9305_init_secondary_channel_324c68(uintptr_t);
uint64_t opencfw_em9305_radio_shift_3027f4(uint32_t,uint32_t,uint32_t);
int main(void)
{
    const uint64_t probe=UINT64_C(0x123456789abcdef0);
    for(unsigned index=0u;index<128u;index++)
        assert(opencfw_em9305_radio_shift_3027f4(
            (uint32_t)probe,(uint32_t)(probe>>32u),index)==
            (probe>>(index&63u)));
    uint8_t channels[48];
    for(unsigned seed=0u;seed<256u;seed++) {
        memset(channels,0xa5,sizeof channels);
        uint64_t mask=((uint64_t)(seed*0x9e3779b9u)<<5u)|
            ((uint64_t)(seed^0x5au)<<32u);
        *(uint32_t *)(void *)channels=(uint32_t)mask;
        *(uint32_t *)(void *)(channels+4u)=(uint32_t)(mask>>32u);
        uint32_t count=0u;
        for(unsigned i=0u;i<37u;i++)if((mask>>i)&1u)count++;
        uint32_t expected=(uint32_t)(uintptr_t)(channels+(count-(((mask>>36u)&1u)!=0u)));
        uint32_t result=opencfw_em9305_init_secondary_channel_324c68(
            (uintptr_t)channels);
        assert(result==expected);
        assert(channels[45]==count);
        unsigned cursor=0u;
        for(unsigned i=0u;i<37u;i++)if((mask>>i)&1u)
            assert(channels[8u+cursor++]==i);
    }
    return 0;
}
