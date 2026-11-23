/* Stock 0x303f80: returns halfword [word[SRAM ((uintptr_t)&em9305_ram_805be0 + 0x38u)]+6].
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t opencfw_em9305_scan_current_303f80(void)
{
  return H16(W32(((uintptr_t)&em9305_ram_805be0 + 0x38u)) + 6u);
}
