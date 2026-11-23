/* Stock 0x327dbc: clears the word at SRAM (uintptr_t)&em9305_ram_805398.
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
void opencfw_em9305_init_transition_refresh_327dbc(void)
{ W32((uintptr_t)&em9305_ram_805398) = 0u; }
