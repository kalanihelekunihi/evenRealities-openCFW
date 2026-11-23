/* Stock 0x325cb4: tail child_325c40(a, 0x10, word[((uintptr_t)&em9305_ram_805c5c + 0x10u)]+4, byte a[692]).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_child_325c40(uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_child_325cb4(uint32_t a)
{
  uint32_t m = B8(a + 692u);
  return opencfw_em9305_child_325c40(a, 0x10u, W32(((uintptr_t)&em9305_ram_805c5c + 0x10u)) + 4u, m);
}
