#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31aa40..0x31aa64: feature gate for opcodes 0x1b/0x1c; they are
 * allowed only when flag bit 2 (0x1b) or bit 1 (0x1c) of ((uintptr_t)&em9305_ram_805a6c + 0x2cu) is set,
 * every other opcode is allowed. */
uint32_t opencfw_em9305_child_31aa40(uint32_t opcode)
{
    if (opcode == 0x1cu)
        return (em9305_ram_805a6c.u8_805a98 >> 1) & 1u;
    if (opcode == 0x1bu)
        return (em9305_ram_805a6c.u8_805a98 >> 2) & 1u;
    return 1u;
}
