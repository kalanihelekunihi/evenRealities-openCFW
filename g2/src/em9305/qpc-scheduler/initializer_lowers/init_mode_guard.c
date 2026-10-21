#include <stdint.h>

/* Complete native 0x31a988..0x31aa3e. Selector is one-based in its
 * nine-entry inline branch table; out-of-range selectors return one. */
uint32_t opencfw_em9305_mode_guard_31a988(uintptr_t context,
                                            uint32_t selector,
                                            uint32_t category)
{
    uint32_t entry=selector-1u;
    if(entry>8u) return 1u;
    switch(entry) {
    case 0u: {
        uint32_t state=*(volatile uint8_t *)(context+2u);
        return state==1u ? (category!=0u) : (category!=4u);
    }
    case 1u:
        if(category!=0u) return 1u;
        if(*(volatile uint8_t *)(context+2u)!=1u) return 1u;
        return (*(volatile uint8_t *)(context+544u)&(1u<<3u))!=0u;
    case 2u: {
        uintptr_t field=context+(category==2u?525u:526u);
        return *(volatile uint8_t *)field==0u;
    }
    case 3u:
        return (*(volatile uint8_t *)(context+544u)&(1u<<5u))!=0u;
    case 4u: {
        uint32_t state=*(volatile uint8_t *)(context+2u);
        if(state==0u) return category!=0u;
        if(category==4u) return 0u;
        if(category!=0u) return 1u;
        return (*(volatile uint8_t *)(context+546u)&1u)!=0u;
    }
    case 5u:
        if(category==4u) return 0u;
        if(category!=0u) return 1u;
        return (*(volatile uint8_t *)(uintptr_t)0x805a97u&1u)!=0u;
    case 6u:
        return (*(volatile uint8_t *)(context+547u)&(1u<<2u))!=0u;
    case 7u:case 8u:
        return (*(volatile uint8_t *)(context+548u)&(1u<<7u))!=0u;
    }
    return 1u;
}
