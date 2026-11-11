#include <stdint.h>

/* Native 0x31aa40..0x31aa64: feature gate for opcodes 0x1b/0x1c; they are
 * allowed only when flag bit 2 (0x1b) or bit 1 (0x1c) of 0x805a98 is set,
 * every other opcode is allowed. */
uint32_t opencfw_em9305_child_31aa40(uint32_t opcode)
{
    if (opcode == 0x1cu)
        return (*(volatile uint8_t *)(uintptr_t)0x805a98u >> 1) & 1u;
    if (opcode == 0x1bu)
        return (*(volatile uint8_t *)(uintptr_t)0x805a98u >> 2) & 1u;
    return 1u;
}
