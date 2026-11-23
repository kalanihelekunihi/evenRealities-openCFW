/* Stock 0x304868: returns 0xff when byte SRAM ((uintptr_t)&em9305_ram_805eec + 0x14u) is 0, else byte SRAM ((uintptr_t)&em9305_ram_8012c0 + 0x3cu).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t opencfw_em9305_associated_child_304868(void)
{
  if(B8(((uintptr_t)&em9305_ram_805eec + 0x14u)) == 0u) return 0xffu;
  return B8(((uintptr_t)&em9305_ram_8012c0 + 0x3cu));
}
