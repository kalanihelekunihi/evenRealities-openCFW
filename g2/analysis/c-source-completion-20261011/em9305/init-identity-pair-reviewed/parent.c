#include <stdint.h>

static uint32_t extract_kind(uint32_t high)
{
#ifdef __arc__
 uint32_t out;__asm__ volatile("xbfu %0,%1,0x10":"=r"(out):"r"(high));return out;
#else
 return (high>>16u)&1u;
#endif
}

/* Complete native 0x31836c..0x3183d0. XBFU 0x10 extracts the single
 * kind bit from the word at third+752. The conditional pair is a native
 * eight-byte stack output, initialized only on the enabled branch. */
extern uint32_t opencfw_em9305_radio_identity_pair_303a60(uint32_t,uint32_t,
    uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_init_callback_child_303918(uint32_t,uint32_t,
    uint32_t,uintptr_t);
uint32_t opencfw_em9305_init_callback_31836c(uintptr_t context,
    uintptr_t settings,uintptr_t third)
{
    uint32_t high=*(volatile uint32_t *)(third+752u);
    uint8_t enabled=*(volatile uint8_t *)(uintptr_t)0x805a9du;
    uint32_t kind=extract_kind(high);
    *(volatile uint8_t *)(context+3u)=(uint8_t)kind;
    if (enabled==0u) return kind;
    uint8_t policy=*(volatile uint8_t *)(uintptr_t)0x805afdu;
    if ((policy&2u)!=0u) {
        uint32_t low=*(volatile uint32_t *)(third+748u);
        volatile uint32_t pair[2];
        pair[1]=0u;
        pair[0]=0u;
        uint32_t found=opencfw_em9305_radio_identity_pair_303a60(kind,low,
            high,(uintptr_t)pair);
        if (found==0u) {
            high=*(volatile uint32_t *)(third+752u);
            low=*(volatile uint32_t *)(third+748u);
            kind=extract_kind(high);
            found=opencfw_em9305_init_callback_child_303918(kind,low,high,
                (uintptr_t)pair);
        }
        (void)found;
        uint32_t upper=pair[1];
        uint32_t lower=pair[0];
        if ((upper|lower)!=0u)
            *(volatile uint8_t *)(context+3u)=1u;
    }
    uint32_t flags=*(volatile uint32_t *)(settings+80u);
    flags|=1u<<6;
    *(volatile uint32_t *)(settings+80u)=flags;
    return flags;
}
