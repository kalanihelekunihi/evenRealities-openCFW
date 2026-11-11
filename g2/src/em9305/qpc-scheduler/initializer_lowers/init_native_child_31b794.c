#include <stdint.h>

/* Native 0x31b794..0x31b7bc: report a capability for selector 1..3;
 * 1 is always supported, 2 and 3 come from bits 0 and 3 of 0x805a95. */
uint32_t opencfw_em9305_child_31b794(uint32_t selector)
{
    if(selector==1u)return 1u;
    if(selector==3u)return (*(volatile uint8_t *)(uintptr_t)0x805a95u>>3)&1u;
    if(selector==2u)return *(volatile uint8_t *)(uintptr_t)0x805a95u&1u;
    return 0u;
}
