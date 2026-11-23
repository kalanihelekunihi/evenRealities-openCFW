#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31b794..0x31b7bc: report a capability for selector 1..3;
 * 1 is always supported, 2 and 3 come from bits 0 and 3 of ((uintptr_t)&em9305_ram_805a6c + 0x29u). */
uint32_t opencfw_em9305_child_31b794(uint32_t selector)
{
    if(selector==1u)return 1u;
    if(selector==3u)return (em9305_ram_805a6c.u8_805a95>>3)&1u;
    if(selector==2u)return em9305_ram_805a6c.u8_805a95&1u;
    return 0u;
}
