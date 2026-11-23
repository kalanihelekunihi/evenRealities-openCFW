/* Stock 0x321820: clears the byte at SRAM ((uintptr_t)&em9305_ram_803d70 + 0x1u).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
void opencfw_em9305_init_secondary_finish_321820(void)
{ B8(((uintptr_t)&em9305_ram_803d70 + 0x1u)) = 0u; }
