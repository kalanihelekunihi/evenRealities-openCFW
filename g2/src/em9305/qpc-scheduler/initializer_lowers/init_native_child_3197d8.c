/* Stock 0x3197d8: p = child_31c500(a); sets byte +109 of p to 1; returns p.
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_child_31c500(uint32_t);
uint32_t opencfw_em9305_child_3197d8(uint32_t a)
{
  uint32_t p = opencfw_em9305_child_31c500(a);
  B8(p + 109u) = 1u;
  return p;
}
